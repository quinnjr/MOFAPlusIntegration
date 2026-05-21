"""
MOFAPlusIntegration PluMA Plugin — wraps mofapy2 for multi-omics factor analysis.

References:
- Argelaguet et al. 2018 (Mol Syst Biol 14:e8124) — original MOFA
- Argelaguet et al. 2020 (Genome Biol 21:111) — MOFA+
- mofapy2: https://github.com/bioFAM/mofapy2 """


from __future__ import annotations
from pathlib import Path
import pandas as pd
from mofapy2.run.entry_point import entry_point


class MOFAPlusIntegration:
    SUPPORTED_MODALITIES = ("transcriptomics", "metagenomics", "metabolomics", "proteomics")

    def __init__(self) -> None:
        self.parameters: dict[str, str] = {}
        self.modalities: dict[str, pd.DataFrame] = {}
        self.subject_ids: list[str] = []
        self.n_factors = 20
        self.max_iter = 1000
        self.convergence_mode = "fast"
        self.scale_views = True
        self.seed = 42
        self.factors: pd.DataFrame | None = None
        self.weights: dict[str, pd.DataFrame] = {}
        self.variance_explained: pd.DataFrame | None = None
        self._model = None

    def input(self, filename: str) -> None:
        # Parse the parameter file (lines like \"key  value\", # comments)

        param_path = Path(filename)

        # Read the parameter file
        with open(param_path, "r") as f:
            for line in f:
                line = line.strip()

                # Skip the empty lines and comments
                if not line or line.startswith("#"):
                    continue
                    
                parts = line.split(maxsplit = 1)

                if len(parts) != 2:
                    continue
                    
                key, value = parts
                self.parameters[key] = value



        # For each supported modality key in self.parameters, load that CSV
        #       with pd.read_csv(path, index_col=0)

        # Load supported modalities
        for modality in self.SUPPORTED_MODALITIES:
            if modality in self.parameters:
                csv_path = Path(self.parameters[modality])

                df = pd.read_csv(csv_path, index_col = 0)
                self.modalities[modality] = df



        # Also support \"modality_<name>\" keys for arbitrary extra views
        for key, value in self.parameters.items():
            if key.startswith("modality_"):
                modality_name = key.removeprefix("modality_")

                df = pd.read_csv(value, index_col = 0)
                self.modalities[modality_name] = df



        # Read hyperparameters (n_factors, max_iter, convergence_mode,
        #       scale_views, seed) if present

        # Hyperparameters
        self.n_factors = int(self.parameters.get("n_factors", self.n_factors))
        self.max_iter = int(self.parameters.get("max_iter", self.max_iter))
        self.convergence_mode = self.parameters.get("convergence_mode", self.convergence_mode)
        self.scale_views = (self.parameters.get("scale_views", str(self.scale_views)).lower() == "true")
        self.seed = int(self.parameters.get("seed", self.seed))


        # Store subject IDs from first modality
        if self.modalities:
            first_df = next(iter(self.modalities.values()))
            self.subject_ids = list(first_df.index)
        

    def run(self) -> None:
        # Align subjects across all modalities (intersection of indices)
        aligned = {}

        shared_subjects = set(self.subject_ids)

        for df in self.modalities.values():
            shared_subjects &= set(df.index)

        shared_subjects = sorted(shared_subjects)

        for modality, df in self.modalities.items():
            aligned[modality] = df.loc[shared_subjects]

        self.subject_ids = shared_subjects


        # Prepare MOFA format
        view_names = sorted(aligned.keys())

        data_list = [
            [aligned[view].values]
            for view in view_names
        ]

        subjects = list(aligned[view_names[0]].index)



        # Build the mofapy2 entry_point and call it (see example below)
        ent = entry_point()

        # Data Options
        ent.set_data_options(scale_groups = False, scale_views = self.scale_views)

        # Set Data Matrix
        ent.set_data_matrix(
            data = data_list,
            likelihoods = ["gaussian"] * len(view_names),
            views_names = view_names,
            groups_names = ["group0"],
            samples_names = [subjects]
        )

        # Model and Train options
        ent.set_model_options(
            factors = self.n_factors
        )

        ent.set_train_options(
            iter = self.max_iter,
            convergence_mode = self.convergence_mode,
            seed = self.seed,
            verbose = False
        )

        # Build, Run and Save the Model
        ent.build()

        ent.run()

        self._model = ent


        # Extract Z (factors) and W (weights) from self._model.model.nodes

        # Z (factors)
        z = self._model.model.nodes["Z"].getExpectation() #type: ignore

        self.factors = pd.DataFrame(
            z,
            index = self.subject_ids,
            columns = [f"Factor{i + 1}" for i in range(z.shape[1])]
        )


        # W (Weights)
        w = self._model.model.nodes["W"].getExpectation() #type: ignore

        self.weights = {}

        for modality, weights_array in zip(view_names, w):

            feature_names = aligned[modality].columns

            self.weights[modality] = pd.DataFrame(
                weights_array,
                index = feature_names,
                columns = [f"Factor{i + 1}" for i in range(weights_array.shape[1])]
            )



        # Extract variance_explained via self._model.model.calculate_variance_explained()
        ve = self._model.model.calculate_variance_explained() #type: ignore

        self.variance_explained = pd.DataFrame(
            ve[0]
        )

        self.variance_explained.columns = [
            f"factor{i + 1}"
            for i in range(len(self.variance_explained.columns))
        ]
        

    def output(self, filename: str) -> None:
        # Write factors to filename.with_suffix(\".factors.csv\")
        base = Path(filename)

        # Save latent factors (Z)
        if self.factors is not None:
            self.factors.to_csv(
                base.with_suffix(".factors.csv")
            )



        # Write each view's weights to filename.with_suffix(f\".weights_{view}.csv\")

        # Save weights (W)
        for view, weights_df in self.weights.items():
            weights_df.to_csv(
                base.with_suffix(f".weights_{view}.csv")
            )




        # Write variance_explained as long-format CSV
        if self.variance_explained is not None:

            self.variance_explained.to_csv(
                base.with_suffix(".variance_explained.csv"),
                index = False
            )



        # Write a human-readable summary text file
        summary_path = base.with_suffix(".summary.txt")

        with open(summary_path, "w") as f:

            f.write("MOFA+ Integration Summary\n")
            f.write("=========================\n\n")

            f.write(f"Number of subjects: {len(self.subject_ids)}\n")
            f.write(f"Number of factors: {self.n_factors}\n")
            f.write(f"Modalities: {', '.join(self.modalities.keys())}\n\n")

            f.write("Feature dimensions per modality:\n")

            for modality, df in self.modalities.items():
                f.write(
                    f" - {modality}: {df.shape[1]} features\n"
                )

            f.write("\nTraining completed successfully.\n")