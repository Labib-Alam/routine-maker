import PyInstaller.__main__
import os
import sys

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))
icon_path = os.path.join(script_dir, 'logo.ico')

PyInstaller.__main__.run([
    'gui_app.py',
    '--onefile',
    '--windowed',
    '--name=Routine_Maker',
    f'--icon={icon_path}',
    '--add-data=routine_data.json;.',
    f'--add-data={icon_path};.',
    '--hidden-import=ttkbootstrap',
    '--hidden-import=pandas',
    '--hidden-import=openpyxl',
    '--clean',
    '--noconfirm'
])
