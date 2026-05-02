#!/bin/bash
echo "============================================"
echo "  LaunchPad - Build Script"
echo "============================================"

echo "[1/3] Installing dependencies..."
pip install -r requirements.txt || { echo "Failed to install dependencies"; exit 1; }

echo "[2/3] Building executable..."
pyinstaller \
  --onefile \
  --windowed \
  --name "LaunchPad" \
  --clean \
  main.py || { echo "Build failed"; exit 1; }

echo "[3/3] Done!"
echo "Executable: dist/LaunchPad"
