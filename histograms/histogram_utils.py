"""Utility functions for working with weight histograms from NanoAOD files."""

import math
import numpy as np
import awkward as ak
import hist
import matplotlib.pyplot as plt
import uproot


def build_weight_histograms(weights, multiplicities, weight_name, valid_multiplicities=None):
    """
    Build histograms for weights by index.

    Args:
        weights: Array of weight values
        multiplicities: Array of weight multiplicities (number of weights per event)
        weight_name: Name of the weight type (e.g., "LHEScaleWeight")
        valid_multiplicities: Optional set of allowed multiplicity values (default: all > 0)

    Returns:
        Dictionary of histograms keyed by weight_name_index
    """
    if valid_multiplicities is None:
        event_mask = multiplicities > 0
    else:
        event_mask = ak.zeros_like(multiplicities, dtype=bool)
        for count in valid_multiplicities:
            event_mask = event_mask | (multiplicities == count)

    selected_weights = weights[event_mask]
    selected_multiplicities = multiplicities[event_mask]
    selected_events = int(ak.sum(event_mask))

    if selected_events == 0:
        print(f"No events selected for {weight_name}")
        return {}

    max_multiplicity = int(ak.max(selected_multiplicities))
    # print(f"{weight_name}: selected events = {selected_events}")
    # print(f"{weight_name}: multiplicity max = {max_multiplicity}")

    histograms = {}
    for index in range(max_multiplicity):
        index_mask = selected_multiplicities > index
        values = ak.to_numpy(selected_weights[index_mask, index])
        hist_name = f"{weight_name}_{index}"
        axis_name = f"{weight_name.lower()}_{index}"
        histograms[hist_name] = hist.Hist(
            hist.axis.Regular(100, 0.0, 2.0, name=axis_name, label=f"{weight_name}[{index}]")
        )
        histograms[hist_name].fill(**{axis_name: values})

    return histograms


def make_lhe_scale_weight_histograms(events):
    """
    Create LHEScaleWeight histograms from NanoAOD events.

    Args:
        events: NanoAOD events object

    Returns:
        Dictionary of LHEScaleWeight histograms
    """
    multiplicities = ak.num(events.LHEScaleWeight, axis=1)
    return build_weight_histograms(
        events.LHEScaleWeight,
        multiplicities,
        "LHEScaleWeight",
        valid_multiplicities={8, 9},
    )


def make_ps_weight_histograms(events):
    """
    Create PSWeight histograms from NanoAOD events.

    Args:
        events: NanoAOD events object

    Returns:
        Dictionary of PSWeight histograms (empty if branch not found)
    """
    if "PSWeight" not in events.fields:
        print("PSWeight branch not found, skipping PSWeight histograms")
        return {}

    if "nPSWeight" in events.fields:
        multiplicities = events.nPSWeight
    else:
        multiplicities = ak.num(events.PSWeight, axis=1)

    return build_weight_histograms(events.PSWeight, multiplicities, "PSWeight")


def save_histograms_to_root(histograms, output_path):
    """
    Save histograms to a ROOT file.

    Args:
        histograms: Dictionary of histograms
        output_path: Output ROOT file path
    """
    with uproot.recreate(output_path) as root_file:
        for name, histogram in histograms.items():
            root_file[name] = histogram


def build_log10_weight_histograms(weights, multiplicities, weight_name, valid_multiplicities=None):
    """
    Build histograms for log10(weights) by index.

    Args:
        weights: Array of weight values
        multiplicities: Array of weight multiplicities (number of weights per event)
        weight_name: Name of the weight type (e.g., "LHEReweightingWeight")
        valid_multiplicities: Optional set of allowed multiplicity values (default: all > 0)

    Returns:
        Dictionary of histograms keyed by weight_name_index
    """
    if valid_multiplicities is None:
        event_mask = multiplicities > 0
    else:
        event_mask = ak.zeros_like(multiplicities, dtype=bool)
        for count in valid_multiplicities:
            event_mask = event_mask | (multiplicities == count)

    selected_weights = weights[event_mask]
    selected_multiplicities = multiplicities[event_mask]
    selected_events = int(ak.sum(event_mask))

    if selected_events == 0:
        print(f"No events selected for {weight_name}")
        return {}

    max_multiplicity = int(ak.max(selected_multiplicities))
    # print(f"{weight_name}: selected events = {selected_events}")
    # print(f"{weight_name}: multiplicity max = {max_multiplicity}")

    histograms = {}
    for index in range(max_multiplicity):
        index_mask = selected_multiplicities > index
        values = ak.to_numpy(selected_weights[index_mask, index])


        # # ---------------- DEBUG AVANT LOG ----------------
        # print(f"\n--- {weight_name}[{index}] ---")
        # print("first 10 raw values:", values[:10])
        # print("min:", np.min(values))
        # print("max:", np.max(values))
        # print("mean:", np.mean(values))

        # # -------------------------------------------------

        # Filter out zero and negative weights before taking log10
        valid_mask = values > 0
        values = values[valid_mask]

        if len(values) == 0:
            print(f"Warning: No positive weights found for {weight_name}[{index}]")
            continue

        log_values = np.log10(values)
        hist_name = f"{weight_name}_{index}"
        axis_name = f"log10_{weight_name.lower()}_{index}"

        # # Auto-scale range based on data
        # log_min = float(np.min(log_values))
        # log_max = float(np.max(log_values))
        # # Add 10% padding
        # log_range = log_max - log_min
        # log_min -= 0.1 * log_range
        # log_max += 0.1 * log_range

        log_min = float(np.min(log_values))
        log_max = float(np.max(log_values))

        log_range = log_max - log_min

        if log_range == 0:
            log_min -= 0.5
            log_max += 0.5
        else:
            log_min -= 0.1 * log_range
            log_max += 0.1 * log_range


        histograms[hist_name] = hist.Hist(
            hist.axis.Regular(100, log_min, log_max, name=axis_name, label=f"log10({weight_name}[{index}])")
        )
        histograms[hist_name].fill(**{axis_name: log_values})

    return histograms


def make_lhe_reweighting_weight_histograms(events):
    """
    Create LHEReweightingWeight histograms (log10-scaled) from NanoAOD events.

    Args:
        events: NanoAOD events object

    Returns:
        Dictionary of LHEReweightingWeight histograms
    """
    if "LHEReweightingWeight" not in events.fields:
        print("LHEReweightingWeight branch not found")
        return {}

    if "nLHEReweightingWeight" in events.fields:
        multiplicities = events.nLHEReweightingWeight
        print(type(events.LHEReweightingWeight))
    else:
        multiplicities = ak.num(events.LHEReweightingWeight, axis=1)

    return build_log10_weight_histograms(
        events.LHEReweightingWeight,
        multiplicities,
        "LHEReweightingWeight",
    )


def build_weighted_observable_histogram(observable, weights, weight_name, n_bins=50, x_min=0, x_max=500):
    """
    Build a histogram for an observable with event weights.

    Args:
        observable: Array of observable values (e.g., pt)
        weights: Array of event weights (1D, one per event)
        weight_name: Name of the histogram
        n_bins: Number of bins
        x_min: Minimum x value
        x_max: Maximum x value

    Returns:
        A histogram object
    """
    if len(observable) == 0:
        print(f"No events available for {weight_name}")
        return None

    axis_name = weight_name.lower()
    histogram = hist.Hist(
        hist.axis.Regular(n_bins, x_min, x_max, name=axis_name, label=weight_name)
    )
    histogram.fill(**{axis_name: observable}, weight=weights)

    return histogram


def get_bosons(events):
    if "GenPart" not in events.fields:
        return ak.Array([])

    gen = events.GenPart

    bosons = gen[(abs(gen.pdgId) == 23) | (abs(gen.pdgId) == 24)]
    bosons = bosons[bosons.hasFlags(["isLastCopy"])]

    return bosons


def get_Z(events):
    gen = events.GenPart
    z = gen[(gen.pdgId == 23)]
    z = z[z.hasFlags(["isLastCopy"])]
    return z


def get_W(events):
    gen = events.GenPart
    w = gen[(abs(gen.pdgId) == 24)]
    w = w[w.hasFlags(["isLastCopy"])]
    return w


def get_has_top(events):
    """
    True per event if a last-copy top or antitop (pdgId == +-6) GenPart is present, i.e. the
    event has real top-quark content and is not a pure VBS diboson event - used to veto
    spurious tZq/ttbar-like contamination that isn't removed by the boson-pair selection.
    """
    if "GenPart" not in events.fields:
        return ak.Array([])

    gen = events.GenPart
    top = gen[abs(gen.pdgId) == 6]
    top = top[top.hasFlags(["isLastCopy"])]
    return ak.num(top, axis=1) > 0

def get_leading_jets(events):
    """
    The two leading GenJets by pt (GenJet is already pt-ordered), with no further
    selection. Returns (j1, j2), both None (per event) where fewer than 2 GenJets exist.
    """
    if "GenJet" not in events.fields:
        return ak.Array([]), ak.Array([])

    jets = events.GenJet
    j1 = ak.firsts(jets)
    j2 = ak.pad_none(jets, 2)[:, 1]
    return j1, j2


def get_mWZ(events):
    z = get_Z(events)
    w = get_W(events)

    z1 = ak.firsts(z)
    w1 = ak.firsts(w)

    valid = ~ak.is_none(z1) & ~ak.is_none(w1)

    return ak.where(valid, (z1 + w1).mass, 0.0)


def get_mVV(events):
    bosons = get_bosons(events)

    bosons = bosons[ak.argsort(bosons.pt, ascending=False)]

    v1 = ak.firsts(bosons)
    v2 = ak.pad_none(bosons, 2)[:, 1]

    valid = ~ak.is_none(v1) & ~ak.is_none(v2)

    return ak.where(valid, (v1 + v2).mass, 0.0)


def get_bosons_by_charge(events, kind, charge=None):
    """
    Select last-copy GenPart bosons of a given kind/charge, pt-sorted (leading first).

    Args:
        kind: "W" or "Z"
        charge: for kind="W", "+" (pdgId==24), "-" (pdgId==-24), or None (either sign).
                Ignored for kind="Z".
    """
    if "GenPart" not in events.fields:
        return ak.Array([])

    gen = events.GenPart
    if kind == "Z":
        mask = gen.pdgId == 23
    elif kind == "W":
        if charge == "+":
            mask = gen.pdgId == 24
        elif charge == "-":
            mask = gen.pdgId == -24
        else:
            mask = abs(gen.pdgId) == 24
    else:
        raise ValueError(f"Unknown boson kind '{kind}', expected 'W' or 'Z'")

    bosons = gen[mask]
    bosons = bosons[bosons.hasFlags(["isLastCopy"])]
    return bosons[ak.argsort(bosons.pt, ascending=False)]


def get_boson_pair(events, kind1, charge1, kind2, charge2):
    """
    The two leading bosons matching (kind1, charge1) and (kind2, charge2), as (v1, v2)
    GenPart records (v1 the higher-pt one). None per-event where not both are found.

    If both requirements select the same collection (e.g. two same-sign W's, or two Z's),
    the leading two bosons of that collection are paired. Otherwise the leading boson of
    each (disjoint) collection is paired (e.g. one W + one Z for a WZ channel).
    """
    same_collection = (kind1, charge1) == (kind2, charge2)

    if same_collection:
        bosons = get_bosons_by_charge(events, kind1, charge1)
        v1 = ak.firsts(bosons)
        v2 = ak.pad_none(bosons, 2)[:, 1]
    else:
        b1 = get_bosons_by_charge(events, kind1, charge1)
        b2 = get_bosons_by_charge(events, kind2, charge2)
        v1 = ak.firsts(b1)
        v2 = ak.firsts(b2)

    return v1, v2


def get_diboson_mass(events, kind1, charge1, kind2, charge2):
    """Invariant mass of the two leading bosons matching (kind1, charge1) and (kind2, charge2)."""
    v1, v2 = get_boson_pair(events, kind1, charge1, kind2, charge2)
    valid = ~ak.is_none(v1) & ~ak.is_none(v2)
    return ak.where(valid, (v1 + v2).mass, np.nan)


def get_leading_boson_pt(events, kind1, charge1, kind2, charge2):
    v1, _ = get_boson_pair(events, kind1, charge1, kind2, charge2)
    return ak.fill_none(v1.pt, np.nan)


def get_subleading_boson_pt(events, kind1, charge1, kind2, charge2):
    _, v2 = get_boson_pair(events, kind1, charge1, kind2, charge2)
    return ak.fill_none(v2.pt, np.nan)


def get_leading_boson_eta(events, kind1, charge1, kind2, charge2):
    v1, _ = get_boson_pair(events, kind1, charge1, kind2, charge2)
    return ak.fill_none(v1.eta, np.nan)


def get_subleading_boson_eta(events, kind1, charge1, kind2, charge2):
    _, v2 = get_boson_pair(events, kind1, charge1, kind2, charge2)
    return ak.fill_none(v2.eta, np.nan)


def get_leading_boson_mass(events, kind1, charge1, kind2, charge2):
    v1, _ = get_boson_pair(events, kind1, charge1, kind2, charge2)
    return ak.fill_none(v1.mass, np.nan)


def get_subleading_boson_mass(events, kind1, charge1, kind2, charge2):
    _, v2 = get_boson_pair(events, kind1, charge1, kind2, charge2)
    return ak.fill_none(v2.mass, np.nan)


def _delta_r(v1, v2):
    dphi = (v1.phi - v2.phi + np.pi) % (2 * np.pi) - np.pi
    deta = v1.eta - v2.eta
    return np.sqrt(deta ** 2 + dphi ** 2)


def get_dR_VV(events, kind1, charge1, kind2, charge2):
    v1, v2 = get_boson_pair(events, kind1, charge1, kind2, charge2)
    valid = ~ak.is_none(v1) & ~ak.is_none(v2)
    return ak.where(valid, _delta_r(v1, v2), np.nan)


def get_vbs_jet1_pt(events):
    j1, _ = get_leading_jets(events)
    return ak.fill_none(j1.pt, 0.0)


def get_vbs_jet2_pt(events):
    _, j2 = get_leading_jets(events)
    return ak.fill_none(j2.pt, 0.0)


def get_vbs_jet1_eta(events):
    j1, _ = get_leading_jets(events)
    return ak.fill_none(j1.eta, 0.0)


def get_vbs_jet2_eta(events):
    _, j2 = get_leading_jets(events)
    return ak.fill_none(j2.eta, 0.0)


def get_dphi_jj(events):
    j1, j2 = get_leading_jets(events)
    valid = ~ak.is_none(j1) & ~ak.is_none(j2)
    dphi = (j1.phi - j2.phi + np.pi) % (2 * np.pi) - np.pi
    return ak.fill_none(ak.where(valid, abs(dphi), 0.0), 0.0)

def get_z_boson_pt(events):
    z = get_Z(events)

    z1 = ak.firsts(z)

    return ak.fill_none(z1.pt, np.nan)

def get_leading_jet_pt(events):
    j1, _ = get_leading_jets(events)
    return ak.fill_none(j1.pt, 0.0)


def get_mjj(events):
    j1, j2 = get_leading_jets(events)

    valid = (~ak.is_none(j1)) & (~ak.is_none(j2))

    mjj = ak.where(
        valid,
        (j1 + j2).mass,
        0.0
    )

    return ak.fill_none(mjj, 0.0)

def get_deta_jj(events):
    j1, j2 = get_leading_jets(events)

    valid = (~ak.is_none(j1)) & (~ak.is_none(j2))

    deta = ak.where(
        valid,
        abs(j1.eta - j2.eta),
        0.0
    )

    return ak.fill_none(deta, 0.0)

def get_z_mass(events):
    z = get_Z(events)
    z1 = ak.firsts(z)
    return ak.fill_none(z1.mass, 0.0)

def get_costheta_star(events):

    if "GenPart" not in events.fields:
        return ak.Array([])

    bosons = events.GenPart[
        (abs(events.GenPart.pdgId) == 23) |
        (abs(events.GenPart.pdgId) == 24)
    ]

    v = ak.firsts(bosons)

    # proxy: use boost direction approximation
    costh = ak.fill_none(v.pz / v.pt, 0.0)

    return costh

def get_z_boson_mass(events):
    """
    Get Z boson mass from GenPart.

    Args:
        events: NanoAOD events object

    Returns:
        Array of Z boson mass values
    """
    if "GenPart" not in events.fields:
        print("GenPart branch not found")
        return ak.Array([])

    gen_particles = events.GenPart
    z_mask = gen_particles.pdgId == 23
    z_bosons = gen_particles[z_mask]

    # Get mass of first Z boson per event
    z_mass = ak.fill_none(ak.firsts(z_bosons.mass), 0)

    return z_mass


def plot_ratio_histograms(hist_numerator, hist_denominator, output_path, title="Observable", hist_numerator_title='EFT (reweighted SM)' ):
    """
    Plot histograms normalized to 1, with ratio panel below.

    Args:
        hist_numerator: Histogram for numerator
        hist_denominator: Histogram for denominator
        output_path: Output PNG file path
        title: Title for the plot
    """
    if hist_numerator is None or hist_denominator is None:
        print("Invalid histograms for ratio plot")
        return

    # Get values and variances
    num_values = hist_numerator.values()
    denom_values = hist_denominator.values()
    num_variances = hist_numerator.variances()
    denom_variances = hist_denominator.variances()

    # Handle None variances
    if num_variances is None:
        num_variances = num_values
    if denom_variances is None:
        denom_variances = denom_values

    # Normalize to 1.0 (divide by integral = sum of bin values * bin width)
    num_integral = np.sum(num_values)
    denom_integral = np.sum(denom_values)

    num_values_norm = num_values / num_integral if num_integral > 0 else num_values
    denom_values_norm = denom_values / denom_integral if denom_integral > 0 else denom_values

    num_variances_norm = num_variances / (num_integral ** 2) if num_integral > 0 else num_variances
    denom_variances_norm = denom_variances / (denom_integral ** 2) if denom_integral > 0 else denom_variances

    # Create figure with ratio panel
    fig = plt.figure(figsize=(10, 8))
    gs = fig.add_gridspec(2, 1, height_ratios=[3, 1], hspace=0.05)
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1], sharex=ax1)

    # Get bin edges for plotting
    axes = hist_numerator.axes
    bin_edges = axes[0].edges
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    bin_width = bin_edges[1] - bin_edges[0]

    # Ensure same shape
    min_bins = min(len(num_values_norm), len(denom_values_norm))
    num_vals = num_values_norm[:min_bins]
    denom_vals = denom_values_norm[:min_bins]
    num_err = np.sqrt(num_variances_norm[:min_bins])
    denom_err = np.sqrt(denom_variances_norm[:min_bins])
    centers = bin_centers[:min_bins]

    # Top panel: normalized histograms
    ax1.step(bin_edges[:min_bins+1], np.concatenate([[num_vals[0]], num_vals]),
             where='mid', label=hist_numerator_title, color='dodgerblue', linewidth=2)
    ax1.step(bin_edges[:min_bins+1], np.concatenate([[denom_vals[0]], denom_vals]),
             where='mid', label='EWK SM', color='purple', linewidth=2, alpha=0.7)
    ax1.errorbar(centers, num_vals, yerr=num_err, fmt='none', ecolor='dodgerblue', alpha=0.5, capsize=3)
    ax1.errorbar(centers, denom_vals, yerr=denom_err, fmt='none', ecolor='purple', alpha=0.5, capsize=3)

    ax1.set_ylabel('Events (normalized to 1.0)')
    ax1.set_title(f'{title} - Normalized to 1.0')
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)

    # Bottom panel: ratio with error bars
    with np.errstate(divide='ignore', invalid='ignore'):
        ratio_vals = np.divide(num_vals, denom_vals, where=(denom_vals > 0), out=np.ones_like(num_vals))
        # Propagate errors: (A/B)^2 * (dA/A)^2 + (dB/B)^2
        ratio_err = np.where(
            denom_vals > 0,
            ratio_vals * np.sqrt((num_err / np.where(num_vals > 0, num_vals, 1)) ** 2 +
                                (denom_err / denom_vals) ** 2),
            0
        )

    ax2.errorbar(centers, ratio_vals, yerr=ratio_err, fmt='o', markersize=6,
                 ecolor='dodgerblue', color='dodgerblue', capsize=4, alpha=0.7)
    ax2.axhline(y=1.0, color='black', linestyle='--', linewidth=2, alpha=0.7)
    ax2.set_ylabel('Ratio')
    ax2.set_xlabel(title)
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_ylim(0.5, 2.0)

    # Hide top x label
    ax1.tick_params(labelbottom=False)

    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(fig)

def plot_each_histograms(histograms, output_prefix):
    """
    Plot all histograms and save them as individual PNG files.

    Args:
        histograms: Dictionary of histograms
        output_prefix: Base path for output files (without extension)
    """
    if not histograms:
        print("No histograms to plot")
        return

    for name, h in histograms.items():
        fig, ax = plt.subplots(figsize=(8, 6))

        # Extract histogram data
        values = h.values()
        variances = h.variances()

        if variances is None:
            variances = values

        errors = np.sqrt(variances)

        # Axis info
        axis = h.axes[0]
        edges = axis.edges
        centers = (edges[:-1] + edges[1:]) / 2

        ax.step(edges, np.append(values, values[-1]), where="post", label=name, linewidth=2)

        ax.errorbar(
            centers,
            values,
            yerr=errors,
            fmt='none',       
            capsize=2,
            linewidth=1.5
        )

        # Labels
        ax.set_xlabel(axis.label if axis.label else axis.name)
        ax.set_ylabel("Entries")
        ax.set_title(name)

        ax.grid(True, alpha=0.3)
        ax.legend()

        # Save per histogram
        output_file = f"{output_prefix}_{name}.png"
        plt.savefig(output_file, dpi=150, bbox_inches="tight")
        plt.close(fig)

        print(f"Saved plot: {output_file}")

def plot_histograms(histograms, output_prefix, lhereweighting=False):
    if not histograms:
        print("No histograms to plot")
        return

    fig, ax = plt.subplots(figsize=(8, 6))

    for name, h in histograms.items():
        values = h.values()
        variances = h.variances()

        if variances is None:
            variances = values

        errors = np.sqrt(variances)
        

        axis = h.axes[0]
        edges = axis.edges
        centers = (edges[:-1] + edges[1:]) / 2


        # Step histogram
        ax.step(
            edges,
            np.append(values, values[-1]),
            where="post",
            linewidth=2,
            label=name
        )

        # Error bars
        ax.errorbar(
            centers,
            values,
            yerr=errors,
            fmt='none',
            capsize=2,
            linewidth=1.5
        )

    ax.set_xlabel(axis.label if axis.label else axis.name)
    ax.set_ylabel("Entries")
    ax.set_title("All histograms")

    ax.grid(True, alpha=0.3)
    ax.legend()

    # --- SPECIAL MODE FOR LHE REWEIGHTING ---
    if lhereweighting:
        ax.set_xlim(-3, 2)
        ax.set_yscale("log")

    output_file = f"{output_prefix}_all.png"
    plt.savefig(output_file, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_normalized_histograms(histograms, output_path, title="Observable", xlabel=None):
    """
    Overlay multiple histograms (e.g. one per channel), each normalized to unit area,
    on a single set of axes. Unlike plot_ratio_histograms this takes an arbitrary number
    of histograms and does not draw a ratio panel.

    Args:
        histograms: dict of {label: histogram} to overlay (None entries are skipped)
        output_path: Output PNG file path
        title: Plot title
        xlabel: X-axis label (defaults to the first histogram's axis label/name)
    """
    histograms = {name: h for name, h in histograms.items() if h is not None}
    if not histograms:
        print("No histograms to plot")
        return

    fig, ax = plt.subplots(figsize=(8, 6))

    axis_label = xlabel
    for name, h in histograms.items():
        values = h.values()
        variances = h.variances()
        if variances is None:
            variances = values

        integral = np.sum(values)
        values_norm = values / integral if integral > 0 else values
        variances_norm = variances / (integral ** 2) if integral > 0 else variances
        errors_norm = np.sqrt(variances_norm)

        axis = h.axes[0]
        edges = axis.edges
        centers = (edges[:-1] + edges[1:]) / 2

        if axis_label is None:
            axis_label = axis.label if axis.label else axis.name

        ax.step(edges, np.append(values_norm, values_norm[-1]), where="post", linewidth=2, label=name)
        ax.errorbar(centers, values_norm, yerr=errors_norm, fmt='none', capsize=2, linewidth=1.2, alpha=0.7)

    ax.set_xlabel(axis_label)
    ax.set_ylabel("Events (normalized to 1.0)")
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend()

    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved plot: {output_path}")