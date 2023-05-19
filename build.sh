pyinstaller --onedir --windowed --icon=./icon.ico --hidden-import=imageio --collect-submodules=pydicom --add-data="./icon.ico;." ImageConverter.py --noconfirm
