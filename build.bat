@echo off
"C:/Users/User/AppData/Local/Programs/Python/Python310/python.exe" -m pip install pyinstaller
"C:/Users/User/AppData/Local/Programs/Python/Python310/python.exe" build.py
echo Done! Check the 'dist' folder for your executable.
pause
