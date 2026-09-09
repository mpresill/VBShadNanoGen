"""Compare generator-level observables between EFT (all reweighting weights) and EWK samples."""

import argparse
import functools
import json
import os
import re
import awkward as ak
import numpy as np

from coffea.nanoevents import NanoEventsFactory, NanoAODSchema

from histogram_utils import (
    build_weighted_observable_histogram,
    get_z_boson_pt,
    plot_ratio_histograms,
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
    get_costheta_star,
    get_has_top,
    get_dR_lhejj,
)
PROCESS = "WMlepZhadJJ"

BASE_INPUT = "/uscms_data/d3/oponcet1/VBS/VBS_NanoGen_EFT/nanogen_files"
BASE_OUTPUT = "/uscms_data/d3/oponcet1/VBS/VBS_NanoGen_EFT/plots"

DEFAULT_INPUT_EFT = os.path.join(BASE_INPUT, PROCESS + "_EWK_SMEFT", PROCESS + "_EWK_SMEFT.root")
DEFAULT_INPUT_EWK = os.path.join(BASE_INPUT, PROCESS + "_EWK_SM", PROCESS + "_EWK_SM.root")

OUTPUT_DIR = os.path.join(BASE_OUTPUT, PROCESS)

# Channel naming convention: <boson1><decay1><boson2><decay2>JJ,
# e.g. WMhadWMhadJJ (W-W-), WPhadZhadJJ (W+Z), ZhadZhadJJ (ZZ), WPMhadZhadJJ (W+Z or W-Z
# combined, charge-inclusive W - matches the "WPM" naming used elsewhere in this repo,
# e.g. crab_submit_files/VBS_WPMZTo4Q..., for the charge-combined W+/-Z sample).
# "WM"/"WP" fix the W charge, "WPM" leaves it inclusive (either sign); decay suffixes
# (had/lep/NuNu) don't affect boson selection.
_BOSON_TOKEN_RE = re.compile(r"(WPM|WM|WP|Z)(had|lep|NuNu)")
_CHARGE_OF = {"WM": "-", "WP": "+", "WPM": None, "Z": None}
_KIND_OF = {"WM": "W", "WP": "W", "WPM": "W", "Z": "Z"}


def parse_channel_bosons(channel_name):
    """
    Parse the two expected bosons (kind, charge) from a channel name, e.g.
    "WMhadWMhadJJ" -> [("W", "-"), ("W", "-")], "WPhadZhadJJ" -> [("W", "+"), ("Z", None)],
    "WPMhadZhadJJ" -> [("W", None), ("Z", None)] (charge-inclusive W).
    """
    tokens = _BOSON_TOKEN_RE.findall(channel_name)
    if len(tokens) != 2:
        raise ValueError(
            f"Could not parse two bosons from channel name '{channel_name}' "
            "(expected two of WM/WP/WPM/Z each followed by had/lep/NuNu)"
        )
    return [(_KIND_OF[token], _CHARGE_OF[token]) for token, _decay in tokens]


def channel_from_input_path(input_path):
    """Derive the channel name from a <channel>_EWK_SMEFT.root / <channel>_EWK_SM.root path."""
    base = os.path.basename(input_path)
    for suffix in ("_EWK_SMEFT.root", "_EWK_SM.root"):
        if base.endswith(suffix):
            return base[: -len(suffix)]
    raise ValueError(f"Could not derive channel name from '{input_path}'")


def build_observables(bosons):
    """Build the OBSERVABLES dict for a given [(kind, charge), (kind, charge)] boson pair."""
    (kind1, charge1), (kind2, charge2) = bosons

    observables = {}

    if kind1 == "Z" or kind2 == "Z":
        observables["z_pt"] = {
            "func": get_z_boson_pt,
            "bins": (50, 0, 500),
            "label": "Z pT (GeV)",
            "boson_func": True,
        }

    if kind1 == "W" and kind2 == "W":
        diboson_name = "mWW"
    elif kind1 == "Z" and kind2 == "Z":
        diboson_name = "mZZ"
    else:
        diboson_name = "mWZ"

    observables[diboson_name] = {
        "func": functools.partial(
            get_diboson_mass, kind1=kind1, charge1=charge1, kind2=kind2, charge2=charge2
        ),
        "bins": (50, 0, 1000),
        "label": f"{diboson_name} (GeV)",
        "boson_func": True,
    }

    boson_kwargs = dict(kind1=kind1, charge1=charge1, kind2=kind2, charge2=charge2)
    observables["V1_pt"] = {
        "func": functools.partial(get_leading_boson_pt, **boson_kwargs),
        "bins": (50, 0, 500),
        "label": "Leading boson pT (GeV)",
        "boson_func": True,
    }
    observables["V2_pt"] = {
        "func": functools.partial(get_subleading_boson_pt, **boson_kwargs),
        "bins": (50, 0, 500),
        "label": "Subleading boson pT (GeV)",
        "boson_func": True,
    }
    observables["V1_eta"] = {
        "func": functools.partial(get_leading_boson_eta, **boson_kwargs),
        "bins": (50, -6, 6),
        "label": "Leading boson eta",
        "boson_func": True,
    }
    observables["V2_eta"] = {
        "func": functools.partial(get_subleading_boson_eta, **boson_kwargs),
        "bins": (50, -6, 6),
        "label": "Subleading boson eta",
        "boson_func": True,
    }
    observables["V1_mass"] = {
        "func": functools.partial(get_leading_boson_mass, **boson_kwargs),
        "bins": (50, 50, 120),
        "label": "Leading boson mass (GeV)",
        "boson_func": True,
    }
    observables["V2_mass"] = {
        "func": functools.partial(get_subleading_boson_mass, **boson_kwargs),
        "bins": (50, 50, 120),
        "label": "Subleading boson mass (GeV)",
        "boson_func": True,
    }
    observables["dR_VV"] = {
        "func": functools.partial(get_dR_VV, **boson_kwargs),
        "bins": (50, 0, 8),
        "label": "delta R(V,V)",
        "boson_func": True,
    }

    observables["leading_jet_pt"] = {
        "func": get_leading_jet_pt,
        "bins": (50, 0, 1000),
        "label": "Leading jet pT (GeV)",
        "boson_func": False,
    }
    observables["mjj"] = {
        "func": get_mjj,
        "bins": (50, 0, 3000),
        "label": "mjj (GeV)",
        "boson_func": False,
    }
    observables["deta_jj"] = {
        "func": get_deta_jj,
        "bins": (50, 0, 8),
        "label": r"delta eta(jj)",
        "boson_func": False,
    }
    observables["dphi_jj"] = {
        "func": get_dphi_jj,
        "bins": (50, 0, 3.2),
        "label": r"delta phi(jj)",
        "boson_func": False,
    }
    observables["vbs_jet1_pt"] = {
        "func": get_vbs_jet1_pt,
        "bins": (50, 0, 1000),
        "label": "VBS jet1 pT (GeV)",
        "boson_func": False,
    }
    observables["vbs_jet2_pt"] = {
        "func": get_vbs_jet2_pt,
        "bins": (50, 0, 500),
        "label": "VBS jet2 pT (GeV)",
        "boson_func": False,
    }
    observables["vbs_jet1_eta"] = {
        "func": get_vbs_jet1_eta,
        "bins": (50, -6, 6),
        "label": "VBS jet1 eta",
        "boson_func": False,
    }
    observables["vbs_jet2_eta"] = {
        "func": get_vbs_jet2_eta,
        "bins": (50, -6, 6),
        "label": "VBS jet2 eta",
        "boson_func": False,
    }

    return observables


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compare generator-level observables for all EFT reweighting weights.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--input-eft", default=DEFAULT_INPUT_EFT)
    parser.add_argument("--input-ewk", default=DEFAULT_INPUT_EWK)
    parser.add_argument("--tree", default="Events")
    parser.add_argument("--output", default="comparison_multiobs")
    parser.add_argument("--output-dir", default=OUTPUT_DIR)
    parser.add_argument(
        "--channel",
        default=None,
        help="Channel name used to select expected boson content/charges (e.g. WMhadWMhadJJ). "
             "Default: parsed from --input-eft's filename.",
    )
    parser.add_argument(
        "--boson-mask",
        action="store_true",
        help="Require the channel's expected boson pair (right charge/kind) to be found. "
             "Off (no selection) by default. Applied event-level: an event failing this is "
             "dropped from EVERY distribution (jet observables included), not just the "
             "boson-kinematic ones.",
    )
    parser.add_argument(
        "--top-veto",
        action="store_true",
        help="Veto events with a real top/antitop (pdgId +-6) GenPart (removes spurious "
             "tZq-like contamination). Off by default; independent of --boson-mask (pass "
             "both for the full selection). Applied event-level, same as --boson-mask.",
    )
    parser.add_argument(
        "--drjj-cut",
        type=float,
        default=None,
        help="Require deltaR between the two leading GenJets to be greater than this value "
             "(e.g. 0.4). Off by default; independent of --boson-mask/--top-veto. Applied "
             "event-level, same as those flags. Events with fewer than 2 GenJets fail this "
             "cut (deltaR undefined).",
    )
    parser.add_argument(
        "--eft-weight-index",
        type=int,
        default=0,
        help="Index into LHEReweightingWeight used as the reference histogram (labeled 'SM' "
             "downstream) that other weights are compared against (default: 0, i.e. "
             "LHEReweightingWeight[0] = SM).",
    )
    return parser.parse_args()


def load_events(input_path, tree_name):
    if ":" in input_path and not input_path.startswith("root://"):
        filespec = input_path
    else:
        filespec = f"{input_path}:{tree_name}"

    return NanoEventsFactory.from_root(
        filespec,
        schemaclass=NanoAODSchema,
    ).events()


def get_output_paths(output_arg):
    return f"{output_arg}.root", output_arg


def main():

    args = parse_args()

    print("\n" + "=" * 80)
    print(f"WARNING: assumes LHEReweightingWeight[{args.eft_weight_index}] = SM")
    print("=" * 80 + "\n")

    channel = args.channel or channel_from_input_path(args.input_eft)
    bosons = parse_channel_bosons(channel)
    observables = build_observables(bosons)
    print(f"Channel: {channel} -> bosons {bosons}")
    print(f"Observables: {list(observables.keys())}")

    print("Loading samples...")
    events_eft = load_events(args.input_eft, args.tree)
    events_ewk = load_events(args.input_ewk, args.tree)

    # EFT weights
    if "LHEReweightingWeight" not in events_eft.fields:
        raise RuntimeError("No LHEReweightingWeight found")

    lhe_weights = events_eft.LHEReweightingWeight
    n_weights = int(ak.num(lhe_weights, axis=1)[0])

    print(f"Number of LHE weights: {n_weights}")

    (kind1, charge1), (kind2, charge2) = bosons
    v1_eft, v2_eft = get_boson_pair(events_eft, kind1, charge1, kind2, charge2)
    v1_ewk, v2_ewk = get_boson_pair(events_ewk, kind1, charge1, kind2, charge2)
    right_sign_eft = ak.to_numpy(~ak.is_none(v1_eft) & ~ak.is_none(v2_eft))
    right_sign_ewk = ak.to_numpy(~ak.is_none(v1_ewk) & ~ak.is_none(v2_ewk))
    print(
        f"Correct-charge boson content ({kind1}{charge1 or ''}, {kind2}{charge2 or ''}): "
        f"EFT {right_sign_eft.sum()}/{len(right_sign_eft)}, EWK {right_sign_ewk.sum()}/{len(right_sign_ewk)}"
    )
    if args.boson_mask:
        print("--boson-mask set: boson-kinematic observables WILL require the channel's "
              "expected boson pair to be found.")

    # Veto events with a real top/antitop (pdgId +-6) in GenPart - removes spurious tZq-like
    # contamination that the boson-pair selection alone doesn't catch. Event-level, applied
    # to EVERY observable when --top-veto is set (independent of --boson-mask).
    no_top_eft = ~ak.to_numpy(get_has_top(events_eft))
    no_top_ewk = ~ak.to_numpy(get_has_top(events_ewk))
    print(
        f"Top-quark veto: EFT {no_top_eft.sum()}/{len(no_top_eft)}, "
        f"EWK {no_top_ewk.sum()}/{len(no_top_ewk)} events would pass (no top/antitop found) "
        f"- {'applied' if args.top_veto else 'NOT applied (pass --top-veto to enable)'}"
    )

    # deltaR(jj) cut on the two leading LHE-level jets (not GenJets - this mirrors the
    # generator run_card's drjj cut). Event-level, applied to EVERY observable when
    # --drjj-cut is set; events with fewer than 2 LHE jets fail (deltaR undefined).
    drjj_eft = ak.to_numpy(get_dR_lhejj(events_eft))
    drjj_ewk = ak.to_numpy(get_dR_lhejj(events_ewk))
    if args.drjj_cut is not None:
        pass_drjj_eft = drjj_eft > args.drjj_cut
        pass_drjj_ewk = drjj_ewk > args.drjj_cut
        print(
            f"deltaR(jj) > {args.drjj_cut} cut (LHE jets): EFT {pass_drjj_eft.sum()}/{len(pass_drjj_eft)}, "
            f"EWK {pass_drjj_ewk.sum()}/{len(pass_drjj_ewk)} events pass - applied"
        )
    else:
        pass_drjj_eft = np.ones(len(drjj_eft), dtype=bool)
        pass_drjj_ewk = np.ones(len(drjj_ewk), dtype=bool)
        print("deltaR(jj) cut (LHE jets): NOT applied (pass --drjj-cut <value> to enable)")

    histograms_all = {}

    os.makedirs(args.output_dir, exist_ok=True)
    root_output, plot_base = get_output_paths(os.path.join(args.output_dir, args.output))

    cutflow = {
        "channel": channel,
        "bosons": f"{kind1}{charge1 or ''}, {kind2}{charge2 or ''}",
        "boson_mask_applied": bool(args.boson_mask),
        "top_veto_applied": bool(args.top_veto),
        "drjj_cut": args.drjj_cut,
        "eft": {
            "n_total": int(len(right_sign_eft)),
            "n_right_sign": int(right_sign_eft.sum()),
            "n_no_top": int(no_top_eft.sum()),
            "n_pass_drjj": int(pass_drjj_eft.sum()),
            "n_right_sign_and_no_top": int((right_sign_eft & no_top_eft).sum()),
        },
        "ewk": {
            "n_total": int(len(right_sign_ewk)),
            "n_right_sign": int(right_sign_ewk.sum()),
            "n_no_top": int(no_top_ewk.sum()),
            "n_pass_drjj": int(pass_drjj_ewk.sum()),
            "n_right_sign_and_no_top": int((right_sign_ewk & no_top_ewk).sum()),
        },
    }
    with open(os.path.join(args.output_dir, "cutflow.json"), "w") as f:
        json.dump(cutflow, f, indent=2)
    print(f"Saved cutflow to {os.path.join(args.output_dir, 'cutflow.json')}")

    with __import__("uproot").recreate(root_output) as root_file:

        for obs_name, cfg in observables.items():

            print(f"\nProcessing observable: {obs_name}")

            func = cfg["func"]
            n_bins, x_min, x_max = cfg["bins"]
            label = cfg["label"]

            values_eft = ak.to_numpy(func(events_eft))
            values_ewk = ak.to_numpy(func(events_ewk))

            # Event-level selections (right-sign boson pair, top veto, deltaR(jj)) are
            # applied to EVERY observable, jet and boson alike: a failing event is dropped
            # from all distributions, not just the boson-kinematic ones.
            mask_eft = ~np.isnan(values_eft)
            mask_ewk = ~np.isnan(values_ewk)
            if args.boson_mask:
                mask_eft = mask_eft & right_sign_eft
                mask_ewk = mask_ewk & right_sign_ewk
            if args.top_veto:
                mask_eft = mask_eft & no_top_eft
                mask_ewk = mask_ewk & no_top_ewk
            if args.drjj_cut is not None:
                mask_eft = mask_eft & pass_drjj_eft
                mask_ewk = mask_ewk & pass_drjj_ewk

            values_eft = values_eft[mask_eft]
            values_ewk = values_ewk[mask_ewk]

            weights_ewk = np.ones_like(values_ewk)

            lhe_weights_obs = lhe_weights[mask_eft]

            sm_weights = ak.to_numpy(
                ak.fill_none(lhe_weights_obs[:, args.eft_weight_index], 1.0)
            )

            histograms = {}

            # SM
            hist_sm = build_weighted_observable_histogram(
                values_eft,
                sm_weights,
                f"{obs_name} (SM)",
                n_bins=n_bins,
                x_min=x_min,
                x_max=x_max,
            )

            # EWK
            hist_ewk = build_weighted_observable_histogram(
                values_ewk,
                weights_ewk,
                f"{obs_name} (EWK)",
                n_bins=n_bins,
                x_min=x_min,
                x_max=x_max,
            )

            histograms["SM"] = hist_sm
            histograms["EWK"] = hist_ewk

            # EFT weights
            for i in range(n_weights):
                weights_i = ak.to_numpy(
                    ak.fill_none(lhe_weights_obs[:, i], 1.0)
                )

                hist_i = build_weighted_observable_histogram(
                    values_eft,
                    weights_i,
                    f"{obs_name} (weight {i})",
                    n_bins=n_bins,
                    x_min=x_min,
                    x_max=x_max,
                )

                histograms[f"weight_{i}"] = hist_i

            # Save ROOT (skip observables with no events on either side)
            for name, hist in histograms.items():
                if hist is None:
                    continue
                root_file[f"{obs_name}_{name}"] = hist
            print("Saved root histo")
            
            # Ratio plots n_weights or 5 first 
            for i in range(1):
                output_file = f"{plot_base}_{obs_name}_weight_{i}.png"

                plot_ratio_histograms(
                    histograms[f"weight_{i}"],
                    hist_ewk,
                    output_file,
                    title=f"{label} (weight {i} / SM)",
                    hist_numerator_title=f"{obs_name}_weight_{i}",
                )

            print(f"Finished {obs_name}")

    print("\nAll observables processed.")


if __name__ == "__main__":
    main()