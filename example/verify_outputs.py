#!/usr/bin/env python3
"""Verify the MOFAPlusIntegration example outputs.

Two checks:

1. **File presence.** The plugin should have emitted the canonical PluMA
   output prefix + suffix shape used in `MOFAPlusIntegration.output()`:
   `.factors.csv`, `.weights_<view>.csv` for every view, `.variance_explained.csv`,
   and `.summary.txt`.

2. **Factor recovery.** MOFA+ recovers latent factors up to sign and
   permutation. For each ground-truth factor in `example/true_factors.csv`,
   we take the maximum |Pearson r| against the recovered factor matrix.
   We require at least 3 of the 5 seeded factors to be recovered with
   |r| ≥ 0.7 — comfortable headroom over chance for this dataset
   (40 subjects, noise σ=0.5).

Usage:

    verify_outputs.py example/out/mofa
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

VIEWS = ("transcriptomics", "metagenomics", "metabolomics", "proteomics")
THRESHOLD = 0.7
MIN_MATCHES = 3


def main(prefix_arg: str) -> int:
    prefix = Path(prefix_arg)
    here = Path(__file__).parent

    expected = [
        prefix.with_suffix(".factors.csv"),
        *(prefix.with_suffix(f".weights_{v}.csv") for v in VIEWS),
        prefix.with_suffix(".variance_explained.csv"),
        prefix.with_suffix(".summary.txt"),
    ]
    missing = [p for p in expected if not p.exists()]
    if missing:
        print("FAIL: missing output files:")
        for p in missing:
            print(f"  - {p}")
        return 1
    print(f"✓ all {len(expected)} expected output files present")

    factors = pd.read_csv(prefix.with_suffix(".factors.csv"), index_col=0)
    truth = pd.read_csv(here / "true_factors.csv", index_col=0)

    common = factors.index.intersection(truth.index)
    if len(common) < 10:
        print(f"FAIL: only {len(common)} subjects in common between recovered and truth")
        return 1
    F = factors.loc[common].values
    T = truth.loc[common].values

    print(
        f"\nFactor recovery on {len(common)} subjects "
        f"({F.shape[1]} recovered vs {T.shape[1]} truth):"
    )
    matched = 0
    for j in range(T.shape[1]):
        best_r, best_k = 0.0, -1
        for k in range(F.shape[1]):
            r = abs(np.corrcoef(F[:, k], T[:, j])[0, 1])
            if not np.isnan(r) and r > best_r:
                best_r, best_k = r, k
        ok = best_r >= THRESHOLD
        marker = "✓" if ok else "✗"
        print(
            f"  truth factor {j}: best |r| = {best_r:.3f} "
            f"(recovered factor {best_k}) {marker}"
        )
        matched += int(ok)

    if matched >= MIN_MATCHES:
        print(
            f"\nPASS: recovered {matched}/{T.shape[1]} true factors "
            f"with |r| >= {THRESHOLD}"
        )
        return 0
    print(
        f"\nFAIL: only recovered {matched}/{T.shape[1]} true factors "
        f"with |r| >= {THRESHOLD} (expected >= {MIN_MATCHES})"
    )
    return 1


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "example/out/mofa"
    sys.exit(main(arg))
