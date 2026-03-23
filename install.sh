#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# L.A.P.H. — User-local installer (NO sudo, XDG-compliant)
# ============================================================

APP_NAME="LAPH"
APP_ID="laph"

INSTALL_ROOT="$HOME/.local"
BIN_DIR="$INSTALL_ROOT/bin"
APP_DIR="$BIN_DIR/LAPH"

SHARE_DIR="$INSTALL_ROOT/share"
DESKTOP_DIR="$SHARE_DIR/applications"
ICON_DIR="$SHARE_DIR/icons/hicolor/256x256/apps"

VENV_DIR="$APP_DIR/venv"
DESKTOP_FILE="$DESKTOP_DIR/$APP_ID.desktop"

# ------------------------------------------------------------
# Installation mode selection
# ------------------------------------------------------------
echo "==> L.A.P.H. Installation Options"
echo
echo "Choose installation mode:"
echo "  1) Full installation (GUI + CLI) - Recommended"
echo "  2) CLI only (command-line interface)"
echo "  3) GUI only (graphical interface)"
echo

read -p "Enter choice [1-3] (default: 1): " choice
choice=${choice:-1}

case $choice in
  1)
    echo "==> Installing full version (GUI + CLI)"
    INSTALL_GUI=true
    INSTALL_CLI=true
    ;;
  2)
    echo "==> Installing CLI only"
    INSTALL_GUI=false
    INSTALL_CLI=true
    ;;
  3)
    echo "==> Installing GUI only"
    INSTALL_GUI=true
    INSTALL_CLI=false
    ;;
  *)
    echo "Invalid choice. Installing full version."
    INSTALL_GUI=true
    INSTALL_CLI=true
    ;;
esac

echo "==> Installing $APP_NAME (user-local)"

# ------------------------------------------------------------
# Sanity checks
# ------------------------------------------------------------
command -v python3 >/dev/null || {
  echo "ERROR: python3 not found"
  exit 1
}

# ------------------------------------------------------------
# Create directories
# ------------------------------------------------------------
mkdir -p "$APP_DIR" "$DESKTOP_DIR" "$ICON_DIR"

# ------------------------------------------------------------
# Copy project files
# ------------------------------------------------------------
echo "==> Copying project files"
if command -v rsync >/dev/null 2>&1; then
  rsync -av \
    --delete \
    --exclude '.git' \
    --exclude 'logs' \
    --exclude 'venv' \
    ./ "$APP_DIR/"
else
  cp -r ./* "$APP_DIR/"
fi

# ------------------------------------------------------------
# Python virtual environment
# ------------------------------------------------------------
echo "==> Creating Python virtual environment"
python3 -m venv "$VENV_DIR"

source "$VENV_DIR/bin/activate"
pip install --upgrade pip

if [[ -f "$APP_DIR/requirements.txt" ]]; then
  echo "==> Installing Python dependencies"
  pip install -r "$APP_DIR/requirements.txt"
fi
deactivate

# ------------------------------------------------------------
# Create launcher scripts
# ------------------------------------------------------------
if [[ "$INSTALL_GUI" == "true" ]]; then
  echo "==> Creating GUI launcher"
  LAUNCHER_BIN="$BIN_DIR/laph"
  cat >"$LAUNCHER_BIN" <<'EOF'
#!/usr/bin/env bash
set -e

APP_VENV="$HOME/.local/bin/LAPH/venv"
"$APP_VENV/bin/python" "$HOME/.local/bin/LAPH/main.py" gui "$@"
EOF
  chmod +x "$LAUNCHER_BIN"
fi

if [[ "$INSTALL_CLI" == "true" ]]; then
  echo "==> Creating CLI launcher"
  LAUNCHER_CLI="$BIN_DIR/laph-cli"
  cat >"$LAUNCHER_CLI" <<'EOF'
#!/usr/bin/env bash
set -e

APP_VENV="$HOME/.local/bin/LAPH/venv"
"$APP_VENV/bin/python" -m core.cli "$@"
EOF
  chmod +x "$LAUNCHER_CLI"
fi

# ------------------------------------------------------------
# Icon installation
# ------------------------------------------------------------
if [[ -f "$APP_DIR/laph_icon.png" ]]; then
  echo "==> Installing icon"
  cp "$APP_DIR/laph_icon.png" "$ICON_DIR/$APP_ID.png"
fi

# ------------------------------------------------------------
# Desktop entry (only for GUI installation)
# ------------------------------------------------------------
if [[ "$INSTALL_GUI" == "true" ]]; then
  echo "==> Creating desktop entry"
  cat >"$DESKTOP_FILE" <<'EOF'
[Desktop Entry]
Type=Application
Name=L.A.P.H.
Comment=Local Autonomous Programming Helper
Exec=laph
Icon=laph
Terminal=false
Categories=Development;Utility;
StartupNotify=true
Keywords=code;generation;ai;programming;
EOF
  chmod 644 "$DESKTOP_FILE"
fi

# ------------------------------------------------------------
# Optional: pull Ollama models
# ------------------------------------------------------------
if command -v ollama >/dev/null 2>&1; then
  if [[ -f "$APP_DIR/configs/models.toml" ]]; then
    echo "==> Pulling Ollama models"
    ollama pull qwen2.5-coder:7b-instruct
    ollama pull qwen3:14b
  fi
fi

# ------------------------------------------------------------
# Desktop database refresh (safe, optional)
# ------------------------------------------------------------
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "$DESKTOP_DIR" >/dev/null 2>&1 || true
fi

echo
echo "✅ $APP_NAME installed successfully"
if [[ "$INSTALL_GUI" == "true" && "$INSTALL_CLI" == "true" ]]; then
  echo "→ GUI: Run 'laph' or launch from app menu"
  echo "→ CLI: Run 'laph-cli' for command-line interface"
elif [[ "$INSTALL_GUI" == "true" ]]; then
  echo "→ GUI: Run 'laph' or launch from app menu"
elif [[ "$INSTALL_CLI" == "true" ]]; then
  echo "→ CLI: Run 'laph-cli' for command-line interface"
fi
echo "→ Uninstall by deleting: $APP_DIR"
if [[ "$INSTALL_GUI" == "true" ]]; then
  echo "  Also delete: $DESKTOP_FILE, $ICON_DIR/$APP_ID.png"
fi
