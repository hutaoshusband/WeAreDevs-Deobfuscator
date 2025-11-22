@echo off
echo Building WeAreDevs Deobfuscator...
echo.

cd /d "%~dp0"
pyinstaller --clean deobfuscator.spec

echo.
echo Builded! Output is in dist/
pause
