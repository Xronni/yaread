#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
ICON_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor/256x256/apps"
PIXMAPS_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/pixmaps"
ICON_SRC="$SCRIPT_DIR/assets/icon.png"

echo "📚 Installing YaRead desktop shortcut..."
mkdir -p "$APP_DIR" "$ICON_DIR" "$PIXMAPS_DIR"

if [ -f "$ICON_SRC" ]; then
    cp "$ICON_SRC" "$ICON_DIR/yaread.png"
    cp "$ICON_SRC" "$PIXMAPS_DIR/yaread.png"
fi

DESKTOP_FILE="$APP_DIR/yaread.desktop"

cat << INNER_EOF > "$DESKTOP_FILE"
[Desktop Entry]
Version=1.0
Type=Application
Name=YaRead
GenericName=AI-Powered PDF Reader
Comment=Intelligent desktop reader with dynamic emotional soundtracks
Path=$SCRIPT_DIR
Exec=/bin/bash "$SCRIPT_DIR/run.sh" %F
Icon=yaread
Terminal=false
Categories=Office;Viewer;AudioVideo;Audio;
MimeType=application/pdf;application/epub+zip;application/x-fictionbook+xml;
StartupWMClass=YaRead
Keywords=pdf;reader;epub;fb2;ai;books;soundtrack;music;
INNER_EOF

chmod +x "$DESKTOP_FILE"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APP_DIR" 2>/dev/null || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t "${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor" 2>/dev/null || true
fi

echo "✅ Installed successfully!"
echo "You can now launch 'YaRead' from your application menu or run: $SCRIPT_DIR/run.sh"
