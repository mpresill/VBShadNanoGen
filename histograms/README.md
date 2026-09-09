# histograms/

Standalone validation/analysis scripts for NanoGEN/NanoAOD ROOT output. These do **not**
require CMSSW; they run in a plain Python virtualenv (coffea/awkward/uproot/hist/matplotlib).
See the top-level `README.md` for how the input ROOT files are generated.

## Setup (one-time)

```sh
python3 -m venv coffea-env
source coffea-env/bin/activate
pip install coffea awkward hist matplotlib uproot fsspec-xrootd XRootD
```

All commands below assume this environment is active and that you are in `histograms/`.
Inputs can be a local path, an `/eos/...` path, or a `root://...` XRootD URL.

## Single-sample checks

- **`lhescale_plot.py`** — LHEScaleWeight (and PSWeight) histograms by index, for one sample.
  ```sh
  python3 lhescale_plot.py --input <file.root> --output <name>
  ```

- **`lhereweighting_plot.py`** — log10(weight) distributions at each EFT reweighting point,
  for one SMEFT sample.
  ```sh
  python3 lhereweighting_plot.py --input <file.root> --output <name>
  ```

Both write `<name>.root` (histograms) and `<name>.png` next to each other.

## SM vs EFT, within one channel

- **`compare_observable.py`** — compares a single observable (Z pT) between an EFT sample
  reweighted to the SM point and the corresponding central EWK/SM sample.
  ```sh
  python3 compare_observable.py --input-eft <smeft.root> --input-ewk <sm.root> --output <name>
  ```

- **`compare_observable_wilsoncoeff.py`** — like above but for every LHE reweighting weight
  and a full set of kinematics (z_pt, mWW/mWZ/mZZ, boson/jet kinematics, mjj, deta_jj,
  dphi_jj). The channel name (parsed from `--input-eft`'s filename, or via `--channel`)
  determines which bosons (W+/W-/Z) are selected — including the charge-inclusive `WPM`
  naming (e.g. `WPMhadZhadJJ` → W of either charge + Z, matching the `crab_submit_files`
  `WPMZTo4Q`-style sample naming).
  ```sh
  python3 compare_observable_wilsoncoeff.py \
      --input-eft <channel>_EWK_SMEFT.root --input-ewk <channel>_EWK_SM.root \
      --output-dir <dir>
  ```

  By default **no selection is applied** (every event is histogrammed; boson observables
  missing their expected pair are filled with 0.0 instead of dropped). Three independent,
  opt-in, event-level selection flags are available — when any is set, an event failing it
  is dropped from **every** distribution (jet observables included, not just the
  boson-kinematic ones):
  - `--boson-mask` — require the channel's expected boson pair (right charge/kind) to be
    found (via `get_boson_pair`).
  - `--top-veto` — veto events with a real top/antitop (`pdgId == +-6`) `GenPart` present
    (`get_has_top`), to remove spurious tZq-like contamination.
  - `--drjj-cut <value>` — require deltaR between the two leading **LHE-level** jets
    (`get_dR_lhejj`, i.e. outgoing `LHEPart` quarks/gluons — not `GenJet`) to exceed
    `<value>` (e.g. `0.4`, mirroring the generator run_card's `drjj` cut).

  Each run also writes `<output-dir>/cutflow.json`, recording per-channel event counts
  (total, right-sign, no-top, drjj-pass) for both EFT and EWK, regardless of which flags
  were actually applied to the histograms — useful for auditing selection efficiency.

- **`compare_all_channels.py`** — runs `compare_observable_wilsoncoeff.py`,
  `lhereweighting_plot.py`, and `lhescale_plot.py` for every channel in its hardcoded
  `CHANNELS` list, by recursively discovering matching `<channel>_EWK_SM/` and
  `<channel>_EWK_SMEFT/` folders (each containing `<channel>_EWK_SM.root` /
  `<channel>_EWK_SMEFT.root`) under `--nanogen-dir` (default: `../nanogen_files`).
  ```sh
  python3 compare_all_channels.py [--channel <name> ...] [--nanogen-dir <dir>] [--output-dir <dir>] [--dry-run]
      [--boson-mask] [--top-veto] [--drjj-cut <value>] [--eft-weight-index <i>]
  ```
  Output goes to `<output-dir>/<category>/<channel>/` (category mirrors any subfolder the
  channel was found under, e.g. `hadronic/`, `semi_leptonic/`). The `--boson-mask`,
  `--top-veto`, `--drjj-cut`, and `--eft-weight-index` flags are passed straight through to
  `compare_observable_wilsoncoeff.py` for every channel. After all channels finish, their
  individual `cutflow.json` files are aggregated into `<output-dir>/cutflow_summary.txt`
  (readable table) and `<output-dir>/cutflow_summary.json`.

  Typical usage to compare selection stages, keeping each in its own directory:
  ```sh
  python3 compare_all_channels.py --output-dir output/no_selection
  python3 compare_all_channels.py --boson-mask --output-dir output/sign_selection
  python3 compare_all_channels.py --drjj-cut 0.4 --output-dir output/drjj_selection
  python3 compare_all_channels.py --boson-mask --top-veto --drjj-cut 0.4 --output-dir output/all_selection
  ```

## SM vs SM, and EFT vs EFT, across channels

- **`compare_channels.py`** — instead of comparing SM to EFT *within* a channel, this
  overlays the **same observable across different channels**: all requested channels' SM
  samples on one plot per observable, and all requested channels' EFT samples (at the SM
  reweighting point) on another. Uses the same channel discovery as `compare_all_channels.py`.
  ```sh
  python3 compare_channels.py [--channel <name> ...] [--nanogen-dir <dir>] [--output-dir <dir>]
      [--boson-mask] [--top-veto] [--drjj-cut <value>] [--extra-sample LABEL:BOSON_CHANNEL:PATH ...]
  ```
  With no `--channel` given, it defaults to the `CHANNELS` list in `compare_all_channels.py`
  (only channels with both SM and SMEFT ROOT files found are used).

  `--extra-sample` (repeatable) adds an SM-group sample that doesn't follow the
  `<channel>_EWK_SM/_EWK_SMEFT` discovery, e.g. a one-off `_LO_EWK` sample: `LABEL` is the
  plot legend entry, `BOSON_CHANNEL` is a channel name (real or not) parsed via
  `parse_channel_bosons()` to pick which W/Z boson kinds/charges to select, and `PATH` is the
  ROOT file. Example:
  ```sh
  python3 compare_channels.py --extra-sample WhadZBBJJ_LO_EWK:WPMhadZhadJJ:../nanogen_files/hadronic/WhadZBBJJ_LO_EWK/WhadZBBJJ_LO_EWK.root
  ```

  Output:
  ```
  <output-dir>/SM/<observable>.png    # one curve per channel, SM sample
  <output-dir>/EFT/<observable>.png   # one curve per channel, EFT sample (SM point)
  ```
  Observables compared (unit-normalized overlays, generic across channels regardless of
  which bosons they contain): `mVV`, `V1_pt`, `V2_pt`, `V1_eta`, `V2_eta`, `V1_mass`,
  `V2_mass`, `dR_VV`, `leading_jet_pt`, `mjj`, `deta_jj`, `dphi_jj`, `vbs_jet1_pt`,
  `vbs_jet2_pt`, `vbs_jet1_eta`, `vbs_jet2_eta`.

  Same selection flags as `compare_observable_wilsoncoeff.py` (`--boson-mask`, `--top-veto`,
  `--drjj-cut`), all off by default, all event-level (a failing event is dropped from every
  observable, jets included, not just boson-kinematic ones).

  Example: compare only the W-W- and W+W+ channels to each other:
  ```sh
  python3 compare_channels.py --channel WMhadWMhadJJ --channel WPhadWPhadJJ
  ```

- **`compare_channels_genlevel.py`** — same structure as `compare_channels.py` (SM-vs-SM,
  EFT-vs-EFT overlays across channels, into `<output-dir>/SM/` and `<output-dir>/EFT/`), but
  plots **unselected** gen-level quantities straight from the `GenJet`/`GenMET`/`GenPart`
  collections instead of the boson-matched/VBS-jet-selected kinematics:
  - `genjet_pt`, `genjet_eta`, `genjet_phi`, `genjet_mass` — filled once per `GenJet`, i.e.
    every jet in every event, no leading/subleading or VBS-pair selection.
  - `w_pt`, `w_eta`, `w_phi`, `w_mass` and `z_pt`, `z_eta`, `z_phi`, `z_mass` — filled once
    per last-copy W or Z `GenPart`, i.e. every W/Z boson found in every event, with no
    charge or pairing requirement (a channel with no Z, e.g. WW, simply contributes no
    entries to the `z_*` plots).
  - `n_genjet`, `genmet_pt`, `genmet_phi` — per event.

  Each channel's legend entry is annotated with its event count, e.g.
  `WMhadWMhadJJ (N=100000)`.
  ```sh
  python3 compare_channels_genlevel.py [--channel <name> ...] [--nanogen-dir <dir>] [--output-dir <dir>]
  ```

## Shared code

`histogram_utils.py` (exported via `__init__.py`) holds the reusable building blocks used
by all scripts above: weight-by-index and log10-weight histogram builders,
LHEScaleWeight/PSWeight/LHEReweightingWeight builders, boson/jet kinematics helpers, and
plotting/I-O helpers. Add new observable/histogram builders here rather than duplicating
logic in a script. Notable helpers:

- `get_boson_pair` / `get_bosons_by_charge` / `get_Z` / `get_W` — last-copy W/Z `GenPart`
  selection (`pdgId == +-24`/`23`, `isLastCopy` flag), pt-sorted; no kinematic (pT/eta) cuts.
- `get_leading_jets` — the two leading `GenJet`s by pt, no selection (plain post-shower
  truth jets; used by `mjj`, `deta_jj`, `dphi_jj`, `leading_jet_pt`, `vbs_jet1/2_pt/eta`).
- `get_lhe_jets` / `get_leading_lhe_jets` / `get_dR_lhejj` — LHE-level jets: outgoing
  (`status == 1`) quark/gluon `LHEPart` records (not `GenJet`), and deltaR between the two
  leading ones. This is the object the generator run_card's `drjj`/`etaj`/`ptj` cuts are
  actually defined on, used by `--drjj-cut`.
- `get_has_top` — True if a real last-copy top/antitop (`pdgId == +-6`) `GenPart` is present
  in the event; used by `--top-veto` to remove spurious tZq-like contamination.
- `plot_normalized_histograms` — overlay an arbitrary number of unit-normalized histograms
  (used by `compare_channels*.py` for the cross-channel comparisons); `plot_ratio_histograms`
  — two histograms with a ratio panel (used by `compare_observable*.py`).
