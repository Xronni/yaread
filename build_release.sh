#!/usr/bin/env bash
# YaRead — Release Artifacts Builder
# Builds .deb package, portable .tar.gz archive, .zip, and SHA256SUMS.txt
set -e

VERSION="1.1.0"
APP_NAME="yaread"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIST_DIR="$SCRIPT_DIR/dist"
RELEASE_DIR="$SCRIPT_DIR/release"
BUILD_DIR="$SCRIPT_DIR/build_artifacts"
PARENT_RELEASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)/release"

echo "================================================================"
echo " 📚 Building Release Artifacts for $APP_NAME v$VERSION"
echo "================================================================"

# Clean up previous builds
rm -rf "$DIST_DIR" "$BUILD_DIR"
mkdir -p "$DIST_DIR" "$BUILD_DIR" "$RELEASE_DIR" "$PARENT_RELEASE_DIR"

# Ensure icon.png exists in assets/
if [ ! -f "$SCRIPT_DIR/assets/icon.png" ]; then
    echo "==> Generating assets/icon.png from icon.ico..."
    python3 -c "
from PIL import Image
im = Image.open('$SCRIPT_DIR/icon.ico')
im.save('$SCRIPT_DIR/assets/icon.png', format='PNG')
"
fi

# 1. Build .deb package
echo "==> 1. Building Debian / Ubuntu (.deb) package..."
DEB_ROOT="$BUILD_DIR/deb_root"
mkdir -p "$DEB_ROOT/DEBIAN"
mkdir -p "$DEB_ROOT/usr/bin"
mkdir -p "$DEB_ROOT/usr/share/$APP_NAME"
mkdir -p "$DEB_ROOT/usr/share/$APP_NAME/assets"
mkdir -p "$DEB_ROOT/usr/share/$APP_NAME/music"
mkdir -p "$DEB_ROOT/usr/share/$APP_NAME/models"
mkdir -p "$DEB_ROOT/usr/share/applications"
mkdir -p "$DEB_ROOT/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$DEB_ROOT/usr/share/pixmaps"

# Control file
cat << CONTROL > "$DEB_ROOT/DEBIAN/control"
Package: $APP_NAME
Version: $VERSION
Section: text
Priority: optional
Architecture: all
Depends: python3 (>= 3.10), python3-pyqt6, python3-pygame, python3-fitz, python3-bs4, python3-lxml, python3-ebooklib
Recommends: python3-pip
Maintainer: Xronni <xronnimail@gmail.com>
Homepage: https://github.com/Xronni/$APP_NAME
Description: AI-Powered PDF Reader with dynamic emotional soundtracks
 YaRead is an intelligent desktop reader that automatically analyzes narrative
 emotional changes using artificial intelligence and synchronizes playback
 of corresponding multi-channel background audio loops. Supports PDF, EPUB,
 and FB2 formats.
CONTROL

# Post-install & Post-remove hooks
cat << 'POSTINST' > "$DEB_ROOT/DEBIAN/postinst"
#!/bin/sh
set -e
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t /usr/share/icons/hicolor || true
fi
exit 0
POSTINST
chmod 755 "$DEB_ROOT/DEBIAN/postinst"

cat << 'POSTRM' > "$DEB_ROOT/DEBIAN/postrm"
#!/bin/sh
set -e
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t /usr/share/icons/hicolor || true
fi
exit 0
POSTRM
chmod 755 "$DEB_ROOT/DEBIAN/postrm"

# Copy application files
cp "$SCRIPT_DIR/yaread.py" "$DEB_ROOT/usr/share/$APP_NAME/"
cp "$SCRIPT_DIR/requirements.txt" "$DEB_ROOT/usr/share/$APP_NAME/"
cp "$SCRIPT_DIR/qr.png" "$DEB_ROOT/usr/share/$APP_NAME/"
cp "$SCRIPT_DIR/icon.ico" "$DEB_ROOT/usr/share/$APP_NAME/"
cp "$SCRIPT_DIR/assets/icon.png" "$DEB_ROOT/usr/share/$APP_NAME/"
cp "$SCRIPT_DIR/assets/icon.png" "$DEB_ROOT/usr/share/$APP_NAME/assets/"
cp "$SCRIPT_DIR/assets/icon.png" "$DEB_ROOT/usr/share/icons/hicolor/256x256/apps/$APP_NAME.png"
cp "$SCRIPT_DIR/assets/icon.png" "$DEB_ROOT/usr/share/pixmaps/$APP_NAME.png"
cp "$SCRIPT_DIR/music"/*.mp3 "$DEB_ROOT/usr/share/$APP_NAME/music/"
if [ -f "$SCRIPT_DIR/models/README.md" ]; then
    cp "$SCRIPT_DIR/models/README.md" "$DEB_ROOT/usr/share/$APP_NAME/models/"
fi

# Executable launcher in /usr/bin
cat << LAUNCHER > "$DEB_ROOT/usr/bin/$APP_NAME"
#!/bin/sh
exec python3 /usr/share/$APP_NAME/yaread.py "\$@"
LAUNCHER
chmod 755 "$DEB_ROOT/usr/bin/$APP_NAME"

# Desktop entry
cat << DESKTOP > "$DEB_ROOT/usr/share/applications/$APP_NAME.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=YaRead
GenericName=AI-Powered PDF Reader
Comment=Intelligent desktop reader with dynamic emotional soundtracks
Exec=/usr/bin/$APP_NAME %F
Icon=$APP_NAME
Terminal=false
Categories=Office;Viewer;AudioVideo;Audio;
MimeType=application/pdf;application/epub+zip;application/x-fictionbook+xml;
StartupWMClass=YaRead
Keywords=pdf;reader;epub;fb2;ai;books;soundtrack;music;
DESKTOP
chmod 644 "$DEB_ROOT/usr/share/applications/$APP_NAME.desktop"

# Fix permissions
find "$DEB_ROOT" -type d -exec chmod 755 {} +
find "$DEB_ROOT/usr/share/$APP_NAME" -type f -exec chmod 644 {} +
chmod 755 "$DEB_ROOT/usr/share/$APP_NAME/yaread.py"

# Build deb
DEB_FILE="$DIST_DIR/${APP_NAME}_${VERSION}_all.deb"
dpkg-deb --build "$DEB_ROOT" "$DEB_FILE"
echo "   ✓ Built: $(basename "$DEB_FILE") ($(du -h "$DEB_FILE" | cut -f1))"

# 2. Build Portable Standalone archives
echo "==> 2. Building Standalone Portable (.tar.gz & .zip) archives..."
TAR_DIR="$BUILD_DIR/${APP_NAME}-${VERSION}"
mkdir -p "$TAR_DIR/assets" "$TAR_DIR/music" "$TAR_DIR/models"

cp "$SCRIPT_DIR/yaread.py" "$TAR_DIR/"
cp "$SCRIPT_DIR/requirements.txt" "$TAR_DIR/"
cp "$SCRIPT_DIR/run.sh" "$TAR_DIR/"
cp "$SCRIPT_DIR/install.sh" "$TAR_DIR/"
cp "$SCRIPT_DIR/uninstall.sh" "$TAR_DIR/"
cp "$SCRIPT_DIR/test.sh" "$TAR_DIR/"
cp "$SCRIPT_DIR/verify_app.py" "$TAR_DIR/"
cp "$SCRIPT_DIR/README.md" "$TAR_DIR/"
cp "$SCRIPT_DIR/LICENSE" "$TAR_DIR/"
cp "$SCRIPT_DIR/icon.ico" "$TAR_DIR/"
cp "$SCRIPT_DIR/qr.png" "$TAR_DIR/"
cp "$SCRIPT_DIR/assets/icon.png" "$TAR_DIR/assets/"
if [ -f "$SCRIPT_DIR/assets/demo.gif" ]; then
    cp "$SCRIPT_DIR/assets/demo.gif" "$TAR_DIR/assets/"
fi
cp "$SCRIPT_DIR/music"/*.mp3 "$TAR_DIR/music/"
if [ -f "$SCRIPT_DIR/models/README.md" ]; then
    cp "$SCRIPT_DIR/models/README.md" "$TAR_DIR/models/"
fi

chmod +x "$TAR_DIR"/*.sh "$TAR_DIR/yaread.py" "$TAR_DIR/verify_app.py"

# Tarball
TAR_FILE="$DIST_DIR/${APP_NAME}-v${VERSION}-linux-x86_64.tar.gz"
tar -czf "$TAR_FILE" -C "$BUILD_DIR" "${APP_NAME}-${VERSION}"
echo "   ✓ Built: $(basename "$TAR_FILE") ($(du -h "$TAR_FILE" | cut -f1))"

TAR_COMPAT="$DIST_DIR/${APP_NAME}-v${VERSION}.tar.gz"
cp "$TAR_FILE" "$TAR_COMPAT"

# Zip archives
ZIP_FILE="$DIST_DIR/${APP_NAME}-v${VERSION}.zip"
(cd "$BUILD_DIR" && zip -q -r "$ZIP_FILE" "${APP_NAME}-${VERSION}")
echo "   ✓ Built: $(basename "$ZIP_FILE") ($(du -h "$ZIP_FILE" | cut -f1))"

ZIP_PORTABLE="$DIST_DIR/${APP_NAME}-v${VERSION}-portable.zip"
cp "$ZIP_FILE" "$ZIP_PORTABLE"

# 3. Generate SHA256 checksums
echo "==> 3. Generating SHA256 Checksums..."
(cd "$DIST_DIR" && sha256sum * > SHA256SUMS.txt)
echo "   ✓ Generated SHA256SUMS.txt"

# 4. Sync to local release/ folders
cp "$DIST_DIR"/* "$RELEASE_DIR/"
cp "$DIST_DIR"/* "$PARENT_RELEASE_DIR/"

# Clean temporary build directory
rm -rf "$BUILD_DIR"

echo "================================================================"
echo " 🎉 All release files successfully built in: dist/ and release/"
ls -lh "$DIST_DIR"
echo "================================================================"
