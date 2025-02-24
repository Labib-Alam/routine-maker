import PyInstaller.__main__

PyInstaller.__main__.run([
    'gui_app.py',
    '--onefile',
    '--windowed',
    '--name=Routine_Maker',
    '--add-data=routine_data.json;.',
    '--hidden-import=ttkbootstrap',
    '--hidden-import=pandas',
    '--hidden-import=openpyxl',
    '--clean',
    '--noconfirm'
])
