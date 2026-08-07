"""Compare generator-level observables between EFT (reweighted SM) and EWK samples."""

import argparse
import os
import awkward as ak
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema

from histogram_utils import (
    build_weighted_observable_histogram,
    get_z_boson_pt,
    save_histograms_to_root,
    plot_ratio_histograms,
)

# DEFAULT_INPUT_EFT = "/eos/cms/store/group/phys_smp/VJets_NLO_VBSanalyses/Samples/NanoAOD/SMEFT/wpzjj_dim6_ewk/2018/wpzjjdim6_ewk_99.root"
# DEFAULT_INPUT_EWK = "/eos/cms/store/group/phys_smp/VJets_NLO_VBSanalyses/Samples/NanoAOD/WplusTo2JZTo2LJJ_EWK_LO_SM_MJJ100PTJ10_TuneCP5_13TeV-madgraph-pythia8/VVjj_2018v6/200810_095240/0000/nano_9.root"

DEFAULT_INPUT_EFT = "/uscms_data/d3/oponcet1/VBS/VBS_NanoGen_EFT/generation/WPhadZNuNuJJ_EWK_SMEFT_nanogen_123.root"
# DEFAULT_INPUT_EWK = "/uscms_data/d3/oponcet1/VBS/VBS_NanoGen_EFT/generation/wpzjjdim6_ewk_99.root"
DEFAULT_INPUT_EWK = "../nanogen_files/hadronic/WMhadZNuNuJJ_EWK_SM/WMhadZNuNuJJ_EWK_SM.root"


def parse_args():
    """Parse command-line arguments."""
    examples = (
        "Examples:\n"
        "  python compare_observable.py\n"
        "  python compare_observable.py --input-eft file1.root --input-ewk file2.root\n"
        "  python compare_observable.py --output my_comparison"
    )
    parser = argparse.ArgumentParser(
        description="Compare generator-level observables between EFT and EWK samples.",
        epilog=examples,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--input-eft",
        default=DEFAULT_INPUT_EFT,
        help="Input SMEFT ROOT file (with reweighting weights)",
    )
    parser.add_argument(
        "--input-ewk",
        default=DEFAULT_INPUT_EWK,
        help="Input EWK ROOT file",
    )
    parser.add_argument(
        "--tree",
        default="Events",
        help="TTree name to read (default: Events)",
    )
    parser.add_argument(
        "--output",
        default="comparison_zpt",
        help="Output basename for files (writes <name>.root and <name>.png)",
    )
    return parser.parse_args()


def load_events(input_path, tree_name):
    """Load NanoAOD events from a ROOT file."""
    if ":" in input_path and not input_path.startswith("root://"):
        filespec = input_path
    else:
        filespec = f"{input_path}:{tree_name}"

    try:
        return NanoEventsFactory.from_root(
            filespec,
            schemaclass=NanoAODSchema,
        ).events()
    except ImportError as exc:
        if input_path.startswith("root://"):
            raise SystemExit(
                "Missing xrootd dependencies for root:// access. Install in your env: "
                "pip install fsspec-xrootd XRootD"
            ) from exc
        raise
    except OSError as exc:
        msg = str(exc)
        if input_path.startswith("root://") and "Operation expired" in msg:
            raise SystemExit(
                "XRootD open timed out, usually due to missing/expired credentials. "
                "Run `voms-proxy-init -voms cms` (or renew your proxy), then retry."
            ) from exc
        raise


def get_output_paths(output_arg):
    """Parse output argument and return .root and .png paths."""
    output_base, output_ext = os.path.splitext(output_arg)
    if output_ext in (".root", ".png"):
        output_base = output_base or "comparison_zpt"
    else:
        output_base = output_arg

    return f"{output_base}.root", f"{output_base}.png"


def get_sm_weights(events):
    """
    Extract SM weights (LHEReweightingWeight[0]) from EFT sample.
    Returns unit weights if not available.
    """
    if "LHEReweightingWeight" not in events.fields:
        print("LHEReweightingWeight not found, using unit weights")
        return ak.ones_like(events.event, dtype=float)

    # Get first reweighting weight (SM) for each event
    lhe_reweighting = events.LHEReweightingWeight
    sm_weights = ak.fill_none(lhe_reweighting[:, 0], 1.0)

    return sm_weights


def main():
    """Main entry point."""
    # Print warning about SM weight assumption
    print("\n" + "="*80)
    print("WARNING: This script assumes that LHEReweightingWeight[0] corresponds to the SM point.")
    print("         Please verify this assumption for your sample!")
    print("="*80 + "\n")

    args = parse_args()

    print("Loading EFT sample...")
    events_eft = load_events(args.input_eft, args.tree)

    print("Loading EWK sample...")
    events_ewk = load_events(args.input_ewk, args.tree)

    # Get observables
    print("Computing Z boson pT for EFT sample...")
    z_pt_eft = get_z_boson_pt(events_eft)

    print("Computing Z boson pT for EWK sample...")
    z_pt_ewk = get_z_boson_pt(events_ewk)

    # Get SM weights for EFT sample
    print("Extracting SM weights from EFT sample...")
    sm_weights = get_sm_weights(events_eft)

    # Convert to numpy for histogram building
    z_pt_eft_np = ak.to_numpy(z_pt_eft)
    z_pt_ewk_np = ak.to_numpy(z_pt_ewk)
    sm_weights_np = ak.to_numpy(sm_weights)

    # Filter out zero pt values
    mask_eft = z_pt_eft_np > 0
    mask_ewk = z_pt_ewk_np > 0

    z_pt_eft_np = z_pt_eft_np[mask_eft]
    sm_weights_np = sm_weights_np[mask_eft]
    z_pt_ewk_np = z_pt_ewk_np[mask_ewk]

    # Create weights for EWK (all 1.0)
    weights_ewk = ak.ones_like(z_pt_ewk_np, dtype=float)

    print(f"EFT events with Z: {len(z_pt_eft_np)}")
    print(f"EWK events with Z: {len(z_pt_ewk_np)}")
    print(f"EFT SM weight range: [{sm_weights_np.min():.4f}, {sm_weights_np.max():.4f}]")
    print(f"EFT weighted integral: {sm_weights_np.sum():.2f}")

    # Build histograms
    print("Building histograms...")
    hist_eft = build_weighted_observable_histogram(
        z_pt_eft_np, sm_weights_np, "Z pT (EFT reweighted SM)", n_bins=50, x_min=0, x_max=500
    )
    hist_ewk = build_weighted_observable_histogram(
        z_pt_ewk_np, weights_ewk, "Z pT (EWK)", n_bins=50, x_min=0, x_max=500
    )

    if hist_eft is None or hist_ewk is None:
        print("Failed to create histograms")
        return

    # Save histograms to ROOT
    root_output, png_output = get_output_paths(args.output)
    histograms = {"Z_pT_EFT": hist_eft, "Z_pT_EWK": hist_ewk}

    with __import__("uproot").recreate(root_output) as root_file:
        for name, histogram in histograms.items():
            root_file[name] = histogram

    print(f"Saved histograms to '{root_output}'")

    # Plot ratio
    print("Creating ratio plot (normalized to 1.0)...")
    plot_ratio_histograms(hist_eft, hist_ewk, png_output, title="Z boson pT (GeV)")
    print(f"Saved plot to '{png_output}'")


if __name__ == "__main__":
    main()
