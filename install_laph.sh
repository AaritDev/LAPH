#!/usr/bin/env bash
set -euo pipefail

# Installer for L.A.P.H. (user-local, no sudo)
# - copies repository to ~/.local/bin/LAPH
# - creates a Python venv and installs requirements
# - optionally pulls models via 'ollama' if available
# - creates a runnable wrapper script
# - creates a .desktop file in ~/.local/share/applications/ (template or from provided file)

PROGNAME="LAPH installer"
INSTALL_DIR="$HOME/.local/bin/LAPH"
DESKTOP_DIR="$HOME/.local/share/applications"
VENV_DIR="$INSTALL_DIR/venv"

usage() {
  cat <<EOF
Usage: $0 [--desktop-file PATH] [--models-only]

Options:
  --desktop-file PATH   Use PATH as the contents for the .desktop file (will copy it into place)
  --models-only         Do not copy files or create venv, only attempt to pull models (requires ollama)
  -h, --help            Show this help

This script performs a user-local install and DOES NOT require sudo. It will
copy the repository into $INSTALL_DIR, create a venv, install Python deps,
and (if available) pull models listed in configs/models.toml using 'ollama'.
EOF
}

DESKTOP_SRC=""
MODELS_ONLY=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --desktop-file)
      DESKTOP_SRC="$2"; shift 2;;
    --models-only)
      MODELS_ONLY=1; shift;;
    -h|--help)
      usage; exit 0;;
    *)
      echo "Unknown arg: $1"; usage; exit 2;;
  esac
done

echo "$PROGNAME: starting"

if [[ $MODELS_ONLY -eq 0 ]]; then
  echo "Creating install directory: $INSTALL_DIR"
  mkdir -p "$INSTALL_DIR"

  echo "Copying project files..."
  # Prefer rsync if available to preserve structure and ignore .git
  if command -v rsync >/dev/null 2>&1; then
    rsync -av --delete --exclude='.git' --exclude='logs' --exclude='venv' ./ "$INSTALL_DIR/"
  else
    # fallback: a conservative copy
    cp -r . "$INSTALL_DIR/"
  fi

  echo "Creating Python virtual environment in $VENV_DIR"
  python3 -m venv "$VENV_DIR"
  # Activate and install requirements
  source "$VENV_DIR/bin/activate"
  if [[ -f "$INSTALL_DIR/requirements.txt" ]]; then
    echo "Installing Python requirements (into venv)..."
    pip install --upgrade pip
    pip install -r "$INSTALL_DIR/requirements.txt"
  else
    echo "No requirements.txt found in $INSTALL_DIR; skipping pip install"
  fi
  deactivate

  # Create a simple launcher script
  cat > "$INSTALL_DIR/run_laph.sh" <<'SH'
#!/usr/bin/env bash
HERE_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$HERE_DIR/venv/bin/activate"
cd "$HERE_DIR"
python main.py
SH
  chmod +x "$INSTALL_DIR/run_laph.sh"
fi

echo "Ensuring desktop applications dir exists: $DESKTOP_DIR"
mkdir -p "$DESKTOP_DIR"

DESKTOP_TARGET="$DESKTOP_DIR/laph.desktop"
if [[ -n "$DESKTOP_SRC" ]]; then
  echo "Using provided .desktop file: $DESKTOP_SRC -> $DESKTOP_TARGET"
  cp "$DESKTOP_SRC" "$DESKTOP_TARGET"
else
  echo "Creating a template .desktop file at $DESKTOP_TARGET"
  cat > "$DESKTOP_TARGET" <<DESK
[Desktop Entry]
Name=LAPH
Comment=Local Autonomous Programming Helper
Exec=python3 $INSTALL_DIR/main.py
Icon=$INSTALL_DIR/laph_icon.png
Terminal=false
Type=Application
Categories=Development
DESK
fi

chmod 644 "$DESKTOP_TARGET"

echo "Attempting to pull models listed in configs/models.toml (requires 'ollama' in PATH)"
if command -v ollama >/dev/null 2>&1; then
  echo "Found ollama: $(command -v ollama)"
  # parse TOML simply for lines like name = "model:tag"
  if [[ -f "$INSTALL_DIR/configs/models.toml" ]]; then
    models=$(grep 'name' "$INSTALL_DIR/configs/models.toml" | sed -E 's/.*=\s*"([^"]+)".*/\1/')
    for m in $models; do
      echo "Pulling model: $m"
      ollama pull "$m" || echo "Failed to pull $m (continuing)"
    done
  else
    echo "No configs/models.toml found in $INSTALL_DIR; skipping model pulls"
  fi
else
  echo "ollama not found in PATH; skipping model pulls."
  echo "To install ollama without sudo, see: https://docs.ollama.ai or install a user-local binary if provided by your platform."
fi

echo "Registering desktop file (no sudo required)."
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database --quiet "$HOME/.local/share/applications" || true
fi

echo "$PROGNAME: finished. You can launch L.A.P.H. from your desktop environment or run: $INSTALL_DIR/run_laph.sh"
echo "If you want me to write your exact .desktop contents, re-run with --desktop-file /path/to/your.desktop"

exit 0
