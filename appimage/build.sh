#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APPIMAGE_DIR="${PROJECT_ROOT}/appimage"
BUILD_DIR="${PROJECT_ROOT}/build"
DIST_DIR="${PROJECT_ROOT}/dist"
APP_NAME="docker-gui"
VERSION="0.1.0"

echo -e "${GREEN}🚀 Starting Docker GUI AppImage build...${NC}"

echo -e "${YELLOW}📋 Checking build dependencies...${NC}"

if ! uv run pyinstaller --version &> /dev/null; then
    echo -e "${RED}❌ PyInstaller not found. Installing...${NC}"
    uv add pyinstaller
fi

if ! command -v appimagetool &> /dev/null; then
    echo -e "${RED}❌ appimagetool not found. Installing...${NC}"
    wget -O appimagetool "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    chmod +x appimagetool
    sudo mv appimagetool /usr/local/bin/
fi

echo -e "${YELLOW}📁 Creating build directories...${NC}"
mkdir -p "${BUILD_DIR}"
mkdir -p "${DIST_DIR}"

echo -e "${YELLOW}🧹 Cleaning previous builds...${NC}"
rm -rf "${BUILD_DIR}"/*
rm -rf "${DIST_DIR}"/*

echo -e "${YELLOW}📝 Creating PyInstaller spec...${NC}"
cat > "${PROJECT_ROOT}/docker-gui.spec" << EOF
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('ui/', 'ui/'),
        ('core/', 'core/'),
        ('services/', 'services/'),
        ('resources/', 'resources/'),
        ('README.md', '.'),
        ('pyproject.toml', '.'),
    ],
    hiddenimports=[
        'gi',
        'gi.repository.Gtk',
        'gi.repository.Gdk',
        'gi.repository.GLib',
        'gi.repository.GObject',
        'gi.repository.Gio',
        'docker',
        'requests',
        'json',
        'threading',
        'queue',
        'psutil',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'jupyter',
        'IPython',
        'notebook',
        'qt5',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='docker-gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='appimage/icon.png' if os.path.exists('appimage/icon.png') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='docker-gui',
)
EOF

echo -e "${YELLOW}🔨 Building with PyInstaller...${NC}"
cd "${PROJECT_ROOT}"
uv run pyinstaller --clean docker-gui.spec

echo -e "${YELLOW}📦 Creating AppDir structure...${NC}"
APPDIR="${BUILD_DIR}/AppDir"
mkdir -p "${APPDIR}/usr/bin"
mkdir -p "${APPDIR}/usr/lib"
mkdir -p "${APPDIR}/usr/share/applications"
mkdir -p "${APPDIR}/usr/share/icons/hicolor/256x256/apps"

echo -e "${YELLOW}📋 Copying PyInstaller output...${NC}"
cp -r "${DIST_DIR}/docker-gui/"* "${APPDIR}/usr/bin/"

echo -e "${YELLOW}📋 Copying desktop file...${NC}"
cp "${APPIMAGE_DIR}/docker-gui.desktop" "${APPDIR}/usr/share/applications/"
cp "${APPIMAGE_DIR}/docker-gui.desktop" "${APPDIR}/"

if [ -f "${APPIMAGE_DIR}/icon.png" ]; then
    echo -e "${YELLOW}📋 Copying icon...${NC}"
    cp "${APPIMAGE_DIR}/icon.png" "${APPDIR}/usr/share/icons/hicolor/256x256/apps/docker-gui.png"
    cp "${APPIMAGE_DIR}/icon.png" "${APPDIR}/docker-gui.png"
fi

echo -e "${YELLOW}📋 Copying AppRun script...${NC}"
cp "${APPIMAGE_DIR}/AppRun" "${APPDIR}/"
chmod +x "${APPDIR}/AppRun"

echo -e "${YELLOW}📦 Creating AppImage...${NC}"
cd "${BUILD_DIR}"
appimagetool AppDir "${DIST_DIR}/${APP_NAME}-${VERSION}-x86_64.AppImage"

# Clean up
echo -e "${YELLOW}🧹 Cleaning up build files...${NC}"
rm -rf "${APPDIR}"
rm -f "${PROJECT_ROOT}/docker-gui.spec"

echo -e "${GREEN}✅ AppImage build completed successfully!${NC}"
echo -e "${GREEN}📦 AppImage location: ${DIST_DIR}/${APP_NAME}-${VERSION}-x86_64.AppImage${NC}"

# Make AppImage executable
chmod +x "${DIST_DIR}/${APP_NAME}-${VERSION}-x86_64.AppImage"

echo -e "${GREEN}🎉 Build process completed!${NC}"
echo -e "${YELLOW}💡 To run the AppImage:${NC}"
echo -e "   ./dist/${APP_NAME}-${VERSION}-x86_64.AppImage" 