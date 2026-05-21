#!/usr/bin/env bash
# Run the MOFAPlusIntegration example through a real pluma binary.
#
# Steps:
#   1. Stage the plugin under a temporary PLUMA_PLUGIN_PATH so pluma can
#      discover MOFAPlusIntegration without needing it installed into the
#      PluMA source tree.
#   2. Invoke pluma against example/config.txt from the repo root.
#   3. Verify the produced CSV/text outputs exist and that the recovered
#      latent factors correlate with the seeded ground truth.
#
# Prereqs:
#   * `pluma` binary on PATH (or pass an explicit path / set PLUMA env var).
#     The binary must be built with `--with-rust` *or* without it — Rust
#     support is unrelated to this Python plugin — but it must have Python
#     plugin support (the default).
#   * `mofapy2`, `numpy`, `pandas`, `h5py` importable from the Python
#     interpreter embedded in pluma. If you're using PluMA's shared venv
#     (resolve_requirements.py), drop a symlink to this repo under
#     <pluma>/plugins/MOFAPlusIntegration/ first and rerun `scons` so
#     mofapy2 lands in the venv automatically.
#
# Usage:
#     ./run_pluma_example.sh                # uses `pluma` from PATH
#     ./run_pluma_example.sh /path/to/pluma # explicit binary
#     PLUMA=/path/to/pluma ./run_pluma_example.sh

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
PLUMA_BIN="${1:-${PLUMA:-pluma}}"

if ! command -v "$PLUMA_BIN" >/dev/null 2>&1 && ! [ -x "$PLUMA_BIN" ]; then
    echo "error: pluma binary not found ('$PLUMA_BIN'). Pass a path or set \$PLUMA." >&2
    exit 1
fi

# Stage the plugin where PluMA's loader can find it
PLUGIN_DIR="$(mktemp -d)"
trap 'rm -rf "$PLUGIN_DIR"' EXIT
mkdir -p "$PLUGIN_DIR/MOFAPlusIntegration"
# PluMA's Python loader globs <dir>/<dir>Plugin.py and instantiates the
# matching <Name>Plugin class; the core module sits beside it so the
# adapter's `from MOFAPlusIntegration import ...` resolves.
ln -sfn "$ROOT/MOFAPlusIntegration.py"       "$PLUGIN_DIR/MOFAPlusIntegration/MOFAPlusIntegration.py"
ln -sfn "$ROOT/MOFAPlusIntegrationPlugin.py" "$PLUGIN_DIR/MOFAPlusIntegration/MOFAPlusIntegrationPlugin.py"

cd "$ROOT"
mkdir -p example/out
rm -f example/out/mofa.*

echo "→ pluma $PLUMA_BIN"
echo "→ plugin staged at $PLUGIN_DIR"
echo "→ running: $PLUMA_BIN example/config.txt"
echo

PLUMA_PLUGIN_PATH="$PLUGIN_DIR" "$PLUMA_BIN" example/config.txt

echo
echo "→ verifying outputs"
python3 "$HERE/verify_outputs.py" example/out/mofa
