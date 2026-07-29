"""Compare generator-level observables between EFT (all reweighting weights) and EWK samples."""

import argparse
import functools
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
)
PROCESS = "WMlepZhadJJ"

BASE_INPUT = "/uscms_data/d3/oponcet1/VBS/VBS_NanoGen_EFT/nanogen_files"
BASE_OUTPUT = "/uscms_data/d3/oponcet1/VBS/VBS_NanoGen_EFT/plots"

DEFAULT_INPUT_EFT = os.path.join(BASE_INPUT, PROCESS + "_EWK_SMEFT", PROCESS + "_EWK_SMEFT.root")
DEFAULT_INPUT_EWK = os.path.join(BASE_INPUT, PROCESS + "_EWK_SM", PROCESS + "_EWK_SM.root")

OUTPUT_DIR = os.path.join(BASE_OUTPUT, PROCESS)

# Channel naming convention: <boson1><decay1><boson2><decay2>JJ,
# e.g. WMhadWMhadJJ (W-W-), WPhadZhadJJ (W+Z), ZhadZhadJJ (ZZ).
# "WM"/"WP" fix the W charge; decay suffixes (had/lep/NuNu) don't affect boson selection.
_BOSON_TOKEN_RE = re.compile(r"(WM|WP|Z)(had|lep|NuNu)")
_CHARGE_OF = {"WM": "-", "WP": "+", "Z": None}
_KIND_OF = {"WM": "W", "WP": "W", "Z": "Z"}


def parse_channel_bosons(channel_name):
    """
    Parse the two expected bosons (kind, charge) from a channel name, e.g.
    "WMhadWMhadJJ" -> [("W", "-"), ("W", "-")], "WPhadZhadJJ" -> [("W", "+"), ("Z", None)].
    """
    tokens = _BOSON_TOKEN_RE.findall(channel_name)
    if len(tokens) != 2:
        raise ValueError(
            f"Could not parse two bosons from channel name '{channel_name}' "
            "(expected two of WM/WP/Z each followed by had/lep/NuNu)"
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
    }

    boson_kwargs = dict(kind1=kind1, charge1=charge1, kind2=kind2, charge2=charge2)
    observables["V1_pt"] = {
        "func": functools.partial(get_leading_boson_pt, **boson_kwargs),
        "bins": (50, 0, 500),
        "label": "Leading boson pT (GeV)",
    }
    observables["V2_pt"] = {
        "func": functools.partial(get_subleading_boson_pt, **boson_kwargs),
        "bins": (50, 0, 500),
        "label": "Subleading boson pT (GeV)",
    }
    observables["V1_eta"] = {
        "func": functools.partial(get_leading_boson_eta, **boson_kwargs),
        "bins": (50, -6, 6),
        "label": "Leading boson eta",
    }
    observables["V2_eta"] = {
        "func": functools.partial(get_subleading_boson_eta, **boson_kwargs),
        "bins": (50, -6, 6),
        "label": "Subleading boson eta",
    }
    observables["V1_mass"] = {
        "func": functools.partial(get_leading_boson_mass, **boson_kwargs),
        "bins": (50, 50, 120),
        "label": "Leading boson mass (GeV)",
    }
    observables["V2_mass"] = {
        "func": functools.partial(get_subleading_boson_mass, **boson_kwargs),
        "bins": (50, 50, 120),
        "label": "Subleading boson mass (GeV)",
    }
    observables["dR_VV"] = {
        "func": functools.partial(get_dR_VV, **boson_kwargs),
        "bins": (50, 0, 8),
        "label": "delta R(V,V)",
    }

    observables["leading_jet_pt"] = {
        "func": get_leading_jet_pt,
        "bins": (50, 0, 1000),
        "label": "Leading jet pT (GeV)",
    }
    observables["mjj"] = {
        "func": get_mjj,
        "bins": (50, 0, 3000),
        "label": "mjj (GeV)",
    }
    observables["deta_jj"] = {
        "func": get_deta_jj,
        "bins": (50, 0, 8),
        "label": r"delta eta(jj)",
    }
    observables["dphi_jj"] = {
        "func": get_dphi_jj,
        "bins": (50, 0, 3.2),
        "label": r"delta phi(jj)",
    }
    observables["vbs_jet1_pt"] = {
        "func": get_vbs_jet1_pt,
        "bins": (50, 0, 1000),
        "label": "VBS jet1 pT (GeV)",
    }
    observables["vbs_jet2_pt"] = {
        "func": get_vbs_jet2_pt,
        "bins": (50, 0, 500),
        "label": "VBS jet2 pT (GeV)",
    }
    observables["vbs_jet1_eta"] = {
        "func": get_vbs_jet1_eta,
        "bins": (50, -6, 6),
        "label": "VBS jet1 eta",
    }
    observables["vbs_jet2_eta"] = {
        "func": get_vbs_jet2_eta,
        "bins": (50, -6, 6),
        "label": "VBS jet2 eta",
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

    print("\n" + "=" * 80)
    print("WARNING: assumes LHEReweightingWeight[0] = SM")
    print("=" * 80 + "\n")

    args = parse_args()

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

    histograms_all = {}

    os.makedirs(args.output_dir, exist_ok=True)
    root_output, plot_base = get_output_paths(os.path.join(args.output_dir, args.output))

    with __import__("uproot").recreate(root_output) as root_file:

        for obs_name, cfg in observables.items():

            print(f"\nProcessing observable: {obs_name}")

            func = cfg["func"]
            n_bins, x_min, x_max = cfg["bins"]
            label = cfg["label"]

            values_eft = ak.to_numpy(func(events_eft))
            values_ewk = ak.to_numpy(func(events_ewk))

            mask_eft = ~np.isnan(values_eft) & right_sign_eft
            mask_ewk = ~np.isnan(values_ewk) & right_sign_ewk

            values_eft = values_eft[mask_eft]
            values_ewk = values_ewk[mask_ewk]

            weights_ewk = np.ones_like(values_ewk)

            lhe_weights_obs = lhe_weights[mask_eft]

            sm_weights = ak.to_numpy(
                ak.fill_none(lhe_weights_obs[:, 0], 1.0)
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