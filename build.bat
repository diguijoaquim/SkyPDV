@echo off
echo 🔥 Compilando com PyInstaller e UPX...
pyinstaller --onefile --noconsole --upx-dir=D:\upx-5.0.0-win64 --add-data "assets;assets" --icon="assets/icon.png" main.py
echo ✅ Build finalizado! Executável está na pasta dist\
pause