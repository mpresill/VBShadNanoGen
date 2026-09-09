"""Plot LHEReweightingWeight (log10-scaled) histograms by index from NanoAOD files."""

import argparse
import os
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema

from histogram_utils import (
    make_lhe_reweighting_weight_histograms,
    save_histograms_to_root,
    plot_histograms,
)

DEFAULT_INPUT = "/eos/cms/store/group/phys_smp/VJets_NLO_VBSanalyses/Samples/NanoAOD/SMEFT/wpzjj_dim6_ewk/2018/wpzjjdim6_ewk_99.root"


def parse_args():
    """Parse command-line arguments."""
    examples = (
        "Examples:\n"
        "  python lhereweighting_plot.py\n"
        "  python lhereweighting_plot.py --input /eos/cms/store/.../file.root\n"
        "  python lhereweighting_plot.py --input root://xrootd-cms.infn.it///store/.../file.root\n"
        "  python lhereweighting_plot.py --input /path/to/custom.root --tree Events\n"
        "  python lhereweighting_plot.py --output my_lhereweighting"
    )
    parser = argparse.ArgumentParser(
        description="Plot LHEReweightingWeight (log10-scaled) histograms by index from NanoAOD files.",
        epilog=examples,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--input",
        default=DEFAULT_INPUT,
        help="Input ROOT file path (local, /eos/..., or root://...)",
    )
    parser.add_argument(
        "--tree",
        default="Events",
        help="TTree name to read (default: Events)",
    )
    parser.add_argument(
        "--output",
        default="lhereweighting_by_index",
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
        output_base = output_base or "lhereweighting_by_index"
    else:
        output_base = output_arg

    return f"{output_base}.root", f"{output_base}.png"


def main():
    """Main entry point."""
    args = parse_args()
    events = load_events(args.input, args.tree)
    root_output, png_output = get_output_paths(args.output)

    # print("events ", events.fields)

    all_hists = make_lhe_reweighting_weight_histograms(events)

    if not all_hists:
        print("No histograms generated. Check that LHEReweightingWeight branch exists.")
        return

    save_histograms_to_root(all_hists, root_output)
    print(f"Saved histograms to '{root_output}'")

    first_hists = dict(list(all_hists.items())[:6])
    print("ok")

    plot_histograms(first_hists, png_output, lhereweighting=True)
    print(f"Saved plot to '{png_output}'")


if __name__ == "__main__":
    main()