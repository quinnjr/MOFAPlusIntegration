import tempfile
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from MOFAPlusIntegration import MOFAPlusIntegration


# Fixture for temp dir
@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


# Fixture plugin
@pytest.fixture
def plugin():
    """Create a plugin instance with example synthetic dataset."""

    plugin = MOFAPlusIntegration()

    plugin.input("example/parameters.txt")

    return plugin



class TestInput:
    """Tests for parameter parsing and modality loading."""

    def test_input_parses_parameters(self, plugin):

        # Ensure all configured omics datasets were loaded
        assert "transcriptomics" in plugin.modalities
        assert "metagenomics" in plugin.modalities
        assert "metabolomics" in plugin.modalities
        assert "proteomics" in plugin.modalities

        # Verify expected number of modalities
        assert len(plugin.modalities) == 4

        # Ensure hyperparameters were parsed correctly
        assert plugin.n_factors == 8
        



@pytest.mark.slow
class TestRun:
    """Tests for MOFA+ model training and latent factor recovery."""

    def test_run_recovers_known_factors(self, plugin):

        # Run MOFA+ training pipeline
        plugin.run()

        # Synthetic dataset includes known latent factors
        true_factors = pd.read_csv(
            "example/true_factors.csv",
            index_col = 0
        )

        recovered = plugin.factors

        matched_factors = 0

        # MOFA factors are sign/order invariant, so compare absolute correlations across all factor pairs
        for true_col in true_factors.columns:

            best_corr = 0

            for recovered_col in recovered.columns:

                corr = np.corrcoef(
                    true_factors[true_col],
                    recovered[recovered_col]
                )[0, 1]

                best_corr = max(best_corr, abs(corr))

            # Count how many true latent factors were successfully recovered
            if best_corr > 0.7:
                matched_factors += 1

        # MOFA should recover at least 3 of the 5 synthetic latent factors
        assert matched_factors >= 3



@pytest.mark.slow
class TestOutput:
    """Tests for output artifact generation."""

    def test_output_writes_expected_files(
        self,
        plugin,
        temp_dir
    ):

        # Run full MOFA+ pipeline before writing outputs
        plugin.run()

        output_path = temp_dir / "output"

        plugin.output(str(output_path))

        # Verify core output file exist
        assert output_path.with_suffix(
            ".factors.csv"
        ).exists()

        assert output_path.with_suffix(
            ".variance_explained.csv"
        ).exists()

        assert output_path.with_suffix(
            ".summary.txt"
        ).exists()


        # Each modality should generate its own weights matrix
        for modality in plugin.modalities.keys():

            assert output_path.with_suffix(
                f".weights_{modality}.csv"
            ).exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
