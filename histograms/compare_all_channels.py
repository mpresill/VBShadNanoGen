"""Run the validation scripts for every channel in CHANNELS that has both SM and SMEFT NanoGEN files.

Recursively scans `nanogen_files/**/<channel>_EWK_SM/<channel>_EWK_SM.root` and
`nanogen_files/**/<channel>_EWK_SMEFT/<channel>_EWK_SMEFT.root` (this matches both a flat
layout and one split into category subfolders, e.g. nanogen_files/hadronic/,
nanogen_files/semi_leptonic/). For every channel in CHANNELS where both merged ROOT files
exist, runs, into `<output-dir>/<category>/<channel>/` (category mirrors the subfolder the
channel was found under, if any):

- compare_observable_wilsoncoeff.py --input-eft <SMEFT> --input-ewk <SM>
  (z_pt, mWW/mWZ/mZZ, boson/jet kinematics, mjj, deta_jj/dphi_jj for every LHE reweighting point)
- lhereweighting_plot.py --input <SMEFT>
- lhescale_plot.py --input <SMEFT>
"""

import argparse
import glob
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
DEFAULT_NANOGEN_DIR = os.path.join(REPO_ROOT, "nanogen_files")
DEFAULT_OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output", "compare_all_channels")
SM_SUFFIX = "_EWK_SM"
SMEFT_SUFFIX = "_EWK_SMEFT"

# Edit this list to control which channels compare_all_channels.py runs on.
CHANNELS = [
    "WMhadWMhadJJ",
    "WMhadZhadJJ",
    "WMhadZlepJJ",
    "WMlepWMhadJJ",
    "WMlepZhadJJ",
    "WPhadWPhadJJ",
    "WPhadZhadJJ",
    "ZhadZhadJJ",
]


def find_channels(nanogen_dir):
    """
    Recursively find <channel>_EWK_SM/ and <channel>_EWK_SMEFT/ subfolders anywhere under
    nanogen_dir. Returns {channel: {"sm": path, "smeft": path, "category": relpath}} for
    channels with both merged ROOT files; category is "." for a flat layout, or the
    subfolder path (e.g. "hadronic") the channel was found under.
    """
    channels = {}

    for path in sorted(glob.glob(os.path.join(nanogen_dir, "**", f"*{SM_SUFFIX}"), recursive=True)):
        channel = os.path.basename(path)[: -len(SM_SUFFIX)]
        root_file = os.path.join(path, f"{channel}{SM_SUFFIX}.root")
        if os.path.isfile(root_file):
            entry = channels.setdefault(channel, {})
            entry["sm"] = root_file
            entry.setdefault("category", os.path.relpath(os.path.dirname(path), nanogen_dir))

    for path in sorted(glob.glob(os.path.join(nanogen_dir, "**", f"*{SMEFT_SUFFIX}"), recursive=True)):
        channel = os.path.basename(path)[: -len(SMEFT_SUFFIX)]
        root_file = os.path.join(path, f"{channel}{SMEFT_SUFFIX}.root")
        if os.path.isfile(root_file):
            entry = channels.setdefault(channel, {})
            entry["smeft"] = root_file
            entry.setdefault("category", os.path.relpath(os.path.dirname(path), nanogen_dir))

    complete = {c: f for c, f in channels.items() if "sm" in f and "smeft" in f}
    incomplete = sorted(c for c, f in channels.items() if c not in complete)
    return complete, incomplete


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
        help="Directory under which a <category>/<channel>/ subfolder is created for each channel's outputs",
    )
    parser.add_argument(
        "--channel",
        action="append",
        dest="channels",
        help="Only run these channel(s) (repeatable), overriding the hardcoded CHANNELS list.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List the channels that would be run without actually running them",
    )
    return parser.parse_args()


def run(cmd, channel, step, failures):
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=SCRIPT_DIR)
    if result.returncode != 0:
        failures.append(f"{channel} ({step})")


def main():
    args = parse_args()
    found, incomplete = find_channels(args.nanogen_dir)

    wanted = args.channels if args.channels else CHANNELS
    missing = [c for c in wanted if c not in found]
    if missing:
        print(f"Requested channel(s) not available (missing SM or SMEFT ROOT file, or not found): {', '.join(missing)}")
    channels = {c: f for c, f in found.items() if c in wanted}

    skipped_incomplete = [c for c in incomplete if c in wanted]
    if skipped_incomplete:
        print(f"Skipping channels missing SM or SMEFT ROOT file: {', '.join(skipped_incomplete)}")

    if not channels:
        print(f"No requested channels with both SM and SMEFT ROOT files found under {args.nanogen_dir}")
        return

    failures = []
    for channel, files in sorted(channels.items()):
        category = files["category"]
        channel_dir = (
            os.path.join(args.output_dir, category, channel)
            if category != "."
            else os.path.join(args.output_dir, channel)
        )
        print(f"\n=== {channel} ({category}) ===")
        print(f"  EFT (SMEFT): {files['smeft']}")
        print(f"  EWK (SM):    {files['sm']}")
        print(f"  -> {channel_dir}/")

        if args.dry_run:
            continue

        os.makedirs(channel_dir, exist_ok=True)

        run(
            [
                sys.executable,
                os.path.join(SCRIPT_DIR, "compare_observable_wilsoncoeff.py"),
                "--input-eft", files["smeft"],
                "--input-ewk", files["sm"],
                "--output-dir", channel_dir,
            ],
            channel, "compare_observable_wilsoncoeff", failures,
        )

        run(
            [
                sys.executable,
                os.path.join(SCRIPT_DIR, "lhereweighting_plot.py"),
                "--input", files["smeft"],
                "--output", os.path.join(channel_dir, f"{channel}_lhereweighting"),
            ],
            channel, "lhereweighting_plot", failures,
        )

        run(
            [
                sys.executable,
                os.path.join(SCRIPT_DIR, "lhescale_plot.py"),
                "--input", files["smeft"],
                "--output", os.path.join(channel_dir, f"{channel}_lhescale"),
            ],
            channel, "lhescale_plot", failures,
        )

    if failures:
        print(f"\nFailed for: {', '.join(failures)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
