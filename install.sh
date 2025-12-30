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
# Launcher script (the ONLY executable entrypoint)
# ------------------------------------------------------------
echo "==> Creating launcher"
cat > "$APP_DIR/laph" <<'EOF'
#!/usr/bin/env bash
set -e

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/venv/bin/activate"
exec python "$HERE/main.py"
EOF

chmod +x "$APP_DIR/laph"
ln -sf "$APP_DIR/laph" "$BIN_DIR/laph"

# ------------------------------------------------------------
# Icon installation
# ------------------------------------------------------------
if [[ -f "$APP_DIR/laph_icon.png" ]]; then
  echo "==> Installing icon"
  cp "$APP_DIR/laph_icon.png" "$ICON_DIR/$APP_ID.png"
fi

# ------------------------------------------------------------
# Desktop entry
# ------------------------------------------------------------
echo "==> Creating desktop entry"
cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=L.A.P.H.
Comment=Local Autonomous Programming Helper
Exec="$APP_DIR/venv/bin/python" "$APP_DIR/main.py"
Icon=$APP_ID
Terminal=true
Categories=Development;Utility;
StartupNotify=true
EOF

chmod 644 "$DESKTOP_FILE"

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
echo "→ Launch from app menu or run: \"$APP_DIR/venv/bin/python $APP_DIR/main.py\" (or run `laph` if your PATH and desktop support it)"
echo "→ Uninstall by deleting: $APP_DIR, $DESKTOP_FILE, $ICON_DIR/$APP_ID.png"