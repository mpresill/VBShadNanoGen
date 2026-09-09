"""Compare raw generator-level quantities between channels, within the SM group and within
the EFT group separately - same structure as compare_channels.py, but plotting unselected
gen-level info straight from the GenJet/GenMET/GenPart collections (every GenJet, and every
last-copy W/Z GenPart, in the event - no leading/VBS-jet or boson-pair-matching selection
applied, unlike compare_channels.py's get_boson_pair-based V1/V2 observables).

Reuses the same <channel>_EWK_SM / <channel>_EWK_SMEFT file discovery as
compare_all_channels.py. For every observable, overlays one unit-normalized histogram per
channel:

    <output-dir>/SM/<obs>.png    - one curve per channel's SM sample
    <output-dir>/EFT/<obs>.png   - one curve per channel's EFT sample (SM reweighting point)

Usage:
    python3 compare_channels_genlevel.py --channel WMhadWMhadJJ --channel WPhadWPhadJJ
    python3 compare_channels_genlevel.py   # defaults to CHANNELS in compare_all_channels.py
"""

import argparse
import os

import awkward as ak
import numpy as np

from coffea.nanoevents import NanoEventsFactory, NanoAODSchema

from compare_all_channels import find_channels, DEFAULT_NANOGEN_DIR, CHANNELS
from histogram_utils import build_weighted_observable_histogram, plot_normalized_histograms, get_W, get_Z

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output", "compare_channels_genlevel")

# Per-object observables: filled once per object in the given (jagged) collection - no
# selection, e.g. every GenJet in every event, or every last-copy W/Z GenPart in every
# event (a channel may have 0, 1, or 2 of these per event depending on its boson content).
COLLECTION_OBSERVABLES = {
    "genjet_pt": {"collection": lambda events: events.GenJet, "field": "pt", "bins": (50, 0, 1000), "label": "GenJet pT (GeV)"},
    "genjet_eta": {"collection": lambda events: events.GenJet, "field": "eta", "bins": (50, -6, 6), "label": "GenJet eta"},
    "genjet_phi": {"collection": lambda events: events.GenJet, "field": "phi", "bins": (50, -3.2, 3.2), "label": "GenJet phi"},
    "genjet_mass": {"collection": lambda events: events.GenJet, "field": "mass", "bins": (50, 0, 50), "label": "GenJet mass (GeV)"},
    "w_pt": {"collection": get_W, "field": "pt", "bins": (50, 0, 500), "label": "W boson pT (GeV)"},
    "w_eta": {"collection": get_W, "field": "eta", "bins": (50, -6, 6), "label": "W boson eta"},
    "w_phi": {"collection": get_W, "field": "phi", "bins": (50, -3.2, 3.2), "label": "W boson phi"},
    "w_mass": {"collection": get_W, "field": "mass", "bins": (50, 50, 120), "label": "W boson mass (GeV)"},
    "z_pt": {"collection": get_Z, "field": "pt", "bins": (50, 0, 500), "label": "Z boson pT (GeV)"},
    "z_eta": {"collection": get_Z, "field": "eta", "bins": (50, -6, 6), "label": "Z boson eta"},
    "z_phi": {"collection": get_Z, "field": "phi", "bins": (50, -3.2, 3.2), "label": "Z boson phi"},
    "z_mass": {"collection": get_Z, "field": "mass", "bins": (50, 50, 120), "label": "Z boson mass (GeV)"},
}

# Per-event observables: filled once per event.
EVENT_OBSERVABLES = {
    "n_genjet": {"func": lambda events: ak.num(events.GenJet, axis=1), "bins": (11, -0.5, 10.5), "label": "Number of GenJets"},
    "genmet_pt": {"func": lambda events: events.GenMET.pt, "bins": (50, 0, 500), "label": "GenMET pT (GeV)"},
    "genmet_phi": {"func": lambda events: events.GenMET.phi, "bins": (50, -3.2, 3.2), "label": "GenMET phi"},
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
    return parser.parse_args()


def load_events(input_path, tree_name):
    filespec = input_path if (":" in input_path and not input_path.startswith("root://")) else f"{input_path}:{tree_name}"
    return NanoEventsFactory.from_root(filespec, schemaclass=NanoAODSchema).events()


def build_group_histograms(channel_events, group_label):
    """
    channel_events: dict of {channel: (events, weights_or_None, n_events)}.
    weights_or_None: per-event weight array, or None for unweighted (SM group).
    n_events: number of events in the sample, appended to the legend label.
    Returns {obs_name: {"<channel> (N=<n_events>)": histogram}}.
    """
    result = {obs_name: {} for obs_name in list(COLLECTION_OBSERVABLES) + list(EVENT_OBSERVABLES)}

    for channel, (events, weights, n_events) in channel_events.items():
        print(f"  [{group_label}] {channel}: computing observables (N={n_events})")
        legend_label = f"{channel} (N={n_events})"

        for obs_name, cfg in COLLECTION_OBSERVABLES.items():
            objects = cfg["collection"](events)
            values = ak.to_numpy(ak.flatten(getattr(objects, cfg["field"])))

            if weights is None:
                w = np.ones_like(values)
            else:
                w_per_obj = ak.broadcast_arrays(ak.Array(weights), objects.pt)[0]
                w = ak.to_numpy(ak.flatten(w_per_obj))

            n_bins, x_min, x_max = cfg["bins"]
            result[obs_name][legend_label] = build_weighted_observable_histogram(
                values, w, f"{obs_name} ({legend_label})", n_bins=n_bins, x_min=x_min, x_max=x_max
            )

        for obs_name, cfg in EVENT_OBSERVABLES.items():
            values = ak.to_numpy(cfg["func"](events))
            w = np.ones_like(values) if weights is None else weights

            n_bins, x_min, x_max = cfg["bins"]
            result[obs_name][legend_label] = build_weighted_observable_histogram(
                values, w, f"{obs_name} ({legend_label})", n_bins=n_bins, x_min=x_min, x_max=x_max
            )

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

    print(f"Comparing channels (gen-level, no selection): {', '.join(sorted(channels))}")

    sm_events = {}
    eft_events = {}
    for channel, files in sorted(channels.items()):
        print(f"Loading {channel}...")
        events_sm = load_events(files["sm"], args.tree)
        events_eft = load_events(files["smeft"], args.tree)

        sm_events[channel] = (events_sm, None, len(events_sm))

        if "LHEReweightingWeight" not in events_eft.fields:
            print(f"  WARNING: {channel} EFT sample has no LHEReweightingWeight, skipping from EFT comparison")
            continue
        sm_point_weights = ak.to_numpy(ak.fill_none(events_eft.LHEReweightingWeight[:, 0], 1.0))
        eft_events[channel] = (events_eft, sm_point_weights, len(events_eft))

    print("\nBuilding SM-group histograms...")
    sm_histograms = build_group_histograms(sm_events, "SM")

    print("\nBuilding EFT-group histograms (SM reweighting point)...")
    eft_histograms = build_group_histograms(eft_events, "EFT")

    all_labels = {**COLLECTION_OBSERVABLES, **EVENT_OBSERVABLES}
    sm_dir = os.path.join(args.output_dir, "SM")
    eft_dir = os.path.join(args.output_dir, "EFT")
    os.makedirs(sm_dir, exist_ok=True)
    os.makedirs(eft_dir, exist_ok=True)

    print("\nPlotting SM channel comparisons...")
    for obs_name, per_channel_hists in sm_histograms.items():
        label = all_labels[obs_name]["label"]
        plot_normalized_histograms(
            per_channel_hists,
            os.path.join(sm_dir, f"{obs_name}.png"),
            title=f"{label} - SM channel comparison (no selection)",
            xlabel=label,
        )

    print("\nPlotting EFT channel comparisons...")
    for obs_name, per_channel_hists in eft_histograms.items():
        label = all_labels[obs_name]["label"]
        plot_normalized_histograms(
            per_channel_hists,
            os.path.join(eft_dir, f"{obs_name}.png"),
            title=f"{label} - EFT channel comparison (SM point, no selection)",
            xlabel=label,
        )

    print(f"\nDone. Plots in {args.output_dir}/SM/ and {args.output_dir}/EFT/")


if __name__ == "__main__":
    main()
