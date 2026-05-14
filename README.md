# MOFAPlusIntegration

A PluMA plugin wrapping [MOFA+](https://github.com/bioFAM/mofapy2) (Multi-Omics Factor Analysis v2) for joint dimensionality reduction across heterogeneous omics modalities.

> **Status: skeleton.** The plugin implementation is not yet written. The repo holds licensing and ignore rules only — see "Planned interface" below.

## Background

MOFA+ decomposes two or more aligned omics matrices (samples × features per modality) into a shared latent factor space plus per-modality feature loadings. Each factor captures co-variation across modalities, so downstream classifiers can regress factor scores against phenotype without paying the cost of high-dimensional, modality-specific feature spaces.

This plugin follows the same convention as sibling integration plugins:

- [SNFIntegration](https://github.com/quinnjr/SNFIntegration) — Similarity Network Fusion
- [SHAPExplainability](https://github.com/quinnjr/SHAPExplainability) — SHAP feature attribution
- [EarlyFusionIntegration](https://github.com/quinnjr/EarlyFusionIntegration) — concatenation + LASSO/ElasticNet selection

## Planned interface

Once implemented, the plugin will follow the PluMA contract used by its siblings:

```
MOFAPlusIntegration.py    # class MOFAPlusIntegration with input()/run()/output()
parameters.mofa.txt       # whitespace key-value parameter file
requirements.txt          # numpy, pandas, mofapy2, h5py
test_mofa_plus_integration.py
```

Inputs: per-modality CSVs (subjects × features). Outputs: factor matrix (subjects × n_factors), per-modality feature weights, variance-explained breakdown, and a training summary.

Synthetic test data with embedded shared latent structure is in [`example/`](example/) — regenerate via `python example/generate_test_data.py`.

## References

- Argelaguet R, Velten B, Hernandez-Cabrera D, et al. (2018). Multi-Omics Factor Analysis — a framework for unsupervised integration of multi-omics data sets. *Mol Syst Biol* 14:e8124. [doi:10.15252/msb.20178124](https://doi.org/10.15252/msb.20178124)
- Argelaguet R, Arnol D, Bredikhin D, et al. (2020). MOFA+: a statistical framework for comprehensive integration of multi-modal single-cell data. *Genome Biol* 21:111. [doi:10.1186/s13059-020-02015-1](https://doi.org/10.1186/s13059-020-02015-1)

## License

MIT — see [LICENSE](LICENSE).
