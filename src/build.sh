#!/bin/bash
echo "Building WeAreDevs Deobfuscator..."
echo

# Change directory to the script's directory
cd "$(dirname "$0")"

pyinstaller --clean deobfuscator.spec

echo
echo "Builded! Output is in dist/"
