"""Generate synthetic multi-omics test data for MOFAPlusIntegration.

Simulates the data-generating process MOFA+ assumes: a small set of
shared latent factors drawn from N(0, 1), then four omics views where
each feature is a linear combination of those factors plus Gaussian
noise. Per-view sparsity in the loadings means each factor is only
"active" in some modalities, which mirrors how MOFA+ tends to be
benchmarked — see Argelaguet et al. 2018 §"Simulation study."

Two groups (case / control) with a slight mean shift on the first
latent factor make the dataset useful for downstream classifier
benchmarks (the groups.csv file maps subjects → group for multi-group
MOFA+ as well).

Run from the repo root:

    python example/generate_test_data.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


N_SUBJECTS = 40
N_TRUE_FACTORS = 5
NOISE_SIGMA = 0.5
SEED = 42

VIEW_SPECS: dict[str, dict[str, object]] = {
    # view_name: { n_features, active_factors (which latent factors load on this view) }
    "transcriptomics": {"n_features": 60, "active_factors": (0, 1, 2)},
    "metagenomics":    {"n_features": 40, "active_factors": (1, 2, 3)},
    "metabolomics":    {"n_features": 30, "active_factors": (0, 3, 4)},
    "proteomics":      {"n_features": 50, "active_factors": (0, 2, 4)},
}

FEATURE_PREFIX = {
    "transcriptomics": "Gene",
    "metagenomics": "Taxa",
    "metabolomics": "Metab",
    "proteomics": "Prot",
}


def main() -> None:
    rng = np.random.default_rng(SEED)
    output_dir = Path(__file__).parent

    subjects = [f"Subject_{i:03d}" for i in range(N_SUBJECTS)]
    # Half case / half control with mean shift on factor 0
    group_labels = np.array(["control"] * (N_SUBJECTS // 2) + ["case"] * (N_SUBJECTS - N_SUBJECTS // 2))
    z = rng.standard_normal(size=(N_SUBJECTS, N_TRUE_FACTORS))
    z[group_labels == "case", 0] += 1.5  # signal lives on factor 0

    written: list[tuple[str, tuple[int, int]]] = []

    for view, spec in VIEW_SPECS.items():
        n_features = int(spec["n_features"])
        active = tuple(spec["active_factors"])  # type: ignore[arg-type]

        # Sparse loadings: only `active` factors contribute, the rest are 0
        loadings = np.zeros((N_TRUE_FACTORS, n_features))
        for f_idx in active:
            loadings[f_idx] = rng.standard_normal(size=n_features) * 1.2

        data = z @ loadings + rng.standard_normal(size=(N_SUBJECTS, n_features)) * NOISE_SIGMA

        prefix = FEATURE_PREFIX[view]
        columns = [f"{prefix}_{i:03d}" for i in range(n_features)]
        df = pd.DataFrame(data, index=subjects, columns=columns)
        df.index.name = "subject_id"

        out_path = output_dir / f"{view}.csv"
        df.to_csv(out_path)
        written.append((view, df.shape))

    # Group assignments (for optional multi-group MOFA+)
    groups_df = pd.DataFrame({"group": group_labels}, index=pd.Index(subjects, name="subject_id"))
    groups_df.to_csv(output_dir / "groups.csv")

    # Ground-truth latent factors so tests can check recovery
    truth_df = pd.DataFrame(
        z,
        index=pd.Index(subjects, name="subject_id"),
        columns=[f"true_factor_{i+1}" for i in range(N_TRUE_FACTORS)],
    )
    truth_df.to_csv(output_dir / "true_factors.csv")

    print(f"Generated synthetic MOFA+ data in {output_dir}:")
    for view, shape in written:
        print(f"  {view}.csv: {shape}")
    print(f"  groups.csv:        {groups_df.shape}")
    print(f"  true_factors.csv:  {truth_df.shape}")
    print(f"Subjects: {N_SUBJECTS}, true latent factors: {N_TRUE_FACTORS}, noise sigma: {NOISE_SIGMA}")


if __name__ == "__main__":
    main()
