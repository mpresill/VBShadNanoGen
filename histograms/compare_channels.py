"""Compare generator-level kinematics between channels, within the SM group and within the
EFT group separately (i.e. SM_channelA vs SM_channelB vs ..., and EFT_channelA vs
EFT_channelB vs ... at the SM reweighting point), rather than SM vs EFT within one channel
(see compare_observable_wilsoncoeff.py for that).

Reuses the same <channel>_EWK_SM / <channel>_EWK_SMEFT file discovery as
compare_all_channels.py. For every observable that is well-defined generically across
channels (leading/subleading boson kinematics, diboson mass, VBS jet kinematics, mjj,
deta_jj, dphi_jj), overlays one unit-normalized histogram per channel:

    <output-dir>/SM/<obs>.png    - one curve per channel's SM sample
    <output-dir>/EFT/<obs>.png   - one curve per channel's EFT sample (SM reweighting point)

Usage:
    python3 compare_channels.py --channel WMhadWMhadJJ --channel WPhadWPhadJJ --channel ZhadZhadJJ
    python3 compare_channels.py   # defaults to CHANNELS in compare_all_channels.py
"""

import argparse
import functools
import os

import awkward as ak
import numpy as np

from coffea.nanoevents import NanoEventsFactory, NanoAODSchema

from compare_all_channels import find_channels, DEFAULT_NANOGEN_DIR, CHANNELS
from compare_observable_wilsoncoeff import parse_channel_bosons
from histogram_utils import (
    build_weighted_observable_histogram,
    plot_normalized_histograms,
    get_boson_pair,
    get_diboson_mass,
    get_leading_boson_pt,
    get_subleading_boson_pt,
    get_leading_boson_eta,
    get_subleading_boson_eta,
    get_leading_boson_mass,
    get_subleading_boson_mass,
    get_dR_VV,
    get_leading_jet_pt,
    get_mjj,
    get_deta_jj,
    get_dphi_jj,
    get_vbs_jet1_pt,
    get_vbs_jet2_pt,
    get_vbs_jet1_eta,
    get_vbs_jet2_eta,
    get_has_top,
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output", "compare_channels")

# Generic observables, defined the same way for every channel regardless of which bosons
# (W+/W-/Z) it contains. Diboson mass is generically labelled "mVV" here since its physical
# meaning (mWW/mWZ/mZZ) differs per channel.
GENERIC_OBSERVABLES = {
    "mVV": {"func": get_diboson_mass, "bins": (50, 0, 1000), "label": "mVV (GeV)", "boson_func": True},
    "V1_pt": {"func": get_leading_boson_pt, "bins": (50, 0, 500), "label": "Leading boson pT (GeV)", "boson_func": True},
    "V2_pt": {"func": get_subleading_boson_pt, "bins": (50, 0, 500), "label": "Subleading boson pT (GeV)", "boson_func": True},
    "V1_eta": {"func": get_leading_boson_eta, "bins": (50, -6, 6), "label": "Leading boson eta", "boson_func": True},
    "V2_eta": {"func": get_subleading_boson_eta, "bins": (50, -6, 6), "label": "Subleading boson eta", "boson_func": True},
    "V1_mass": {"func": get_leading_boson_mass, "bins": (50, 50, 120), "label": "Leading boson mass (GeV)", "boson_func": True},
    "V2_mass": {"func": get_subleading_boson_mass, "bins": (50, 50, 120), "label": "Subleading boson mass (GeV)", "boson_func": True},
    "dR_VV": {"func": get_dR_VV, "bins": (50, 0, 8), "label": "delta R(V,V)", "boson_func": True},
    "leading_jet_pt": {"func": get_leading_jet_pt, "bins": (50, 0, 1000), "label": "Leading jet pT (GeV)", "boson_func": False},
    "mjj": {"func": get_mjj, "bins": (50, 0, 3000), "label": "mjj (GeV)", "boson_func": False},
    "deta_jj": {"func": get_deta_jj, "bins": (50, 0, 8), "label": r"delta eta(jj)", "boson_func": False},
    "dphi_jj": {"func": get_dphi_jj, "bins": (50, 0, 3.2), "label": r"delta phi(jj)", "boson_func": False},
    "vbs_jet1_pt": {"func": get_vbs_jet1_pt, "bins": (50, 0, 1000), "label": "VBS jet1 pT (GeV)", "boson_func": False},
    "vbs_jet2_pt": {"func": get_vbs_jet2_pt, "bins": (50, 0, 500), "label": "VBS jet2 pT (GeV)", "boson_func": False},
    "vbs_jet1_eta": {"func": get_vbs_jet1_eta, "bins": (50, -6, 6), "label": "VBS jet1 eta", "boson_func": False},
    "vbs_jet2_eta": {"func": get_vbs_jet2_eta, "bins": (50, -6, 6), "label": "VBS jet2 eta", "boson_func": False},
}


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--nanogen-dir",
        default=DEFAULT_NANOGEN_DIR,
        help="Directory to recursively search for <channel>_EWK_SM/ and <channel>_EWK_SMEFT/ subfolders",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="Directory in which SM/ and EFT/ subfolders of comparison plots are created",
    )
    parser.add_argument(
        "--channel",
        action="append",
        dest="channels",
        help="Channel(s) to compare (repeatable). Default: CHANNELS from compare_all_channels.py",
    )
    parser.add_argument("--tree", default="Events")
    parser.add_argument(
        "--boson-mask",
        action="store_true",
        help="Require the channel's expected boson pair (right charge/kind) to be found. "
             "Off (no selection) by default. Event-level: a failing event is dropped from "
             "EVERY distribution (jet observables included), not just the boson-kinematic "
             "ones. With this off, boson observables missing their pair are filled with 0.0 "
             "instead of dropping the event.",
    )
    parser.add_argument(
        "--top-veto",
        action="store_true",
        help="Veto events with a real top/antitop (pdgId +-6) GenPart (removes spurious "
             "tZq-like contamination). Off by default; independent of --boson-mask (pass "
             "both for the full selection). Applied event-level, same as --boson-mask.",
    )
    return parser.parse_args()


def load_events(input_path, tree_name):
    filespec = input_path if (":" in input_path and not input_path.startswith("root://")) else f"{input_path}:{tree_name}"
    return NanoEventsFactory.from_root(filespec, schemaclass=NanoAODSchema).events()


def compute_observable(obs_name, cfg, events, boson_kwargs):
    func = cfg["func"]
    values = func(events, **boson_kwargs) if cfg["boson_func"] else func(events)
    return ak.to_numpy(values)


def build_group_histograms(channel_events, group_label, apply_boson_mask=False, apply_top_veto=False):
    """
    channel_events: dict of {channel: (events, boson_kwargs, weights_or_None)}.
    weights_or_None: per-event weight array, or None for unweighted (SM group).
    apply_boson_mask: if True, require the channel's expected boson pair (right charge/kind)
        to be found. apply_top_veto: if True, veto events with a real top/antitop GenPart
        (tZq-like contamination). Both off by default (no selection). These are event-level
        cuts: a failing event is dropped from EVERY observable's histogram (jets included),
        not just the boson-kinematic ones. With neither flag set, boson observables that
        would be NaN (missing pair) are filled with 0.0 instead of dropping the event.
    Returns {obs_name: {channel: histogram}}.
    """
    result = {obs_name: {} for obs_name in GENERIC_OBSERVABLES}
    any_selection = apply_boson_mask or apply_top_veto

    for channel, (events, boson_kwargs, weights) in channel_events.items():
        print(f"  [{group_label}] {channel}: computing observables")

        combined_mask = None
        if any_selection:
            n_events = len(events)
            combined_mask = np.ones(n_events, dtype=bool)
            if apply_boson_mask:
                v1, v2 = get_boson_pair(events, **boson_kwargs)
                right_sign = ak.to_numpy(~ak.is_none(v1) & ~ak.is_none(v2))
                combined_mask &= right_sign
                print(f"    right-sign boson pair: {right_sign.sum()}/{n_events} events kept")
            if apply_top_veto:
                no_top = ~ak.to_numpy(get_has_top(events))
                combined_mask &= no_top
                print(f"    top-quark veto: {no_top.sum()}/{n_events} events kept")
            print(f"    combined selection: {combined_mask.sum()}/{n_events} events kept")

        for obs_name, cfg in GENERIC_OBSERVABLES.items():
            values = compute_observable(obs_name, cfg, events, boson_kwargs)

            if any_selection:
                mask = ~np.isnan(values) & combined_mask
                values = values[mask]
                w = np.ones_like(values) if weights is None else weights[mask]
            else:
                values = np.nan_to_num(values, nan=0.0)
                w = np.ones_like(values) if weights is None else weights

            n_bins, x_min, x_max = cfg["bins"]
            hist_ = build_weighted_observable_histogram(
                values, w, f"{obs_name} ({channel})", n_bins=n_bins, x_min=x_min, x_max=x_max
            )
            result[obs_name][channel] = hist_

    return result


def main():
    args = parse_args()
    found, incomplete = find_channels(args.nanogen_dir)

    wanted = args.channels if args.channels else CHANNELS
    missing = [c for c in wanted if c not in found]
    if missing:
        print(f"Requested channel(s) not available (missing SM or SMEFT ROOT file, or not found): {', '.join(missing)}")
    channels = {c: f for c, f in found.items() if c in wanted}

    if not channels:
        print(f"No requested channels with both SM and SMEFT ROOT files found under {args.nanogen_dir}")
        return

    print(f"Comparing channels: {', '.join(sorted(channels))}")

    sm_events = {}
    eft_events = {}
    for channel, files in sorted(channels.items()):
        bosons = parse_channel_bosons(channel)
        (kind1, charge1), (kind2, charge2) = bosons
        boson_kwargs = dict(kind1=kind1, charge1=charge1, kind2=kind2, charge2=charge2)

        print(f"Loading {channel}...")
        events_sm = load_events(files["sm"], args.tree)
        events_eft = load_events(files["smeft"], args.tree)

        sm_events[channel] = (events_sm, boson_kwargs, None)

        if "LHEReweightingWeight" not in events_eft.fields:
            print(f"  WARNING: {channel} EFT sample has no LHEReweightingWeight, skipping from EFT comparison")
            continue
        sm_point_weights = ak.to_numpy(ak.fill_none(events_eft.LHEReweightingWeight[:, 0], 1.0))
        eft_events[channel] = (events_eft, boson_kwargs, sm_point_weights)

    if not args.boson_mask and not args.top_veto:
        print("\nNo selection flags set: no events dropped (missing boson pairs filled with 0.0).")
    else:
        print(
            f"\nSelection: boson-mask={'on' if args.boson_mask else 'off'}, "
            f"top-veto={'on' if args.top_veto else 'off'} - failing events dropped from "
            "every distribution."
        )

    print("\nBuilding SM-group histograms...")
    sm_histograms = build_group_histograms(sm_events, "SM", args.boson_mask, args.top_veto)

    print("\nBuilding EFT-group histograms (SM reweighting point)...")
    eft_histograms = build_group_histograms(eft_events, "EFT", args.boson_mask, args.top_veto)

    sm_dir = os.path.join(args.output_dir, "SM")
    eft_dir = os.path.join(args.output_dir, "EFT")
    os.makedirs(sm_dir, exist_ok=True)
    os.makedirs(eft_dir, exist_ok=True)

    print("\nPlotting SM channel comparisons...")
    for obs_name, per_channel_hists in sm_histograms.items():
        label = GENERIC_OBSERVABLES[obs_name]["label"]
        plot_normalized_histograms(
            per_channel_hists,
            os.path.join(sm_dir, f"{obs_name}.png"),
            title=f"{label} - SM channel comparison",
            xlabel=label,
        )

    print("\nPlotting EFT channel comparisons...")
    for obs_name, per_channel_hists in eft_histograms.items():
        label = GENERIC_OBSERVABLES[obs_name]["label"]
        plot_normalized_histograms(
            per_channel_hists,
            os.path.join(eft_dir, f"{obs_name}.png"),
            title=f"{label} - EFT channel comparison (SM point)",
            xlabel=label,
        )

    print(f"\nDone. Plots in {args.output_dir}/SM/ and {args.output_dir}/EFT/")


if __name__ == "__main__":
    main()
