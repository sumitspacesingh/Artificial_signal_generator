@echo off
echo Installing dependencies...
pip install -r requirements.txt
echo Building executable...
pip install pyinstaller
pyinstaller --onefile --windowed signal_generator_app.py
echo Done.
echo Your application is in the dist folder.
pause
