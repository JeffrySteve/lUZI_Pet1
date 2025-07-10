import os
import PyInstaller.__main__
import shutil

def build_exe():
    # Define paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(current_dir, 'dist')
    assets_dir = os.path.join(current_dir, 'assets')
    
    # Clean previous builds
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    
    # Build executable
    PyInstaller.__main__.run([
        'pet.py',
        '--onefile',
        '--windowed',
        '--name=VirtualCat',
        '--add-data=assets;assets',
        '--icon=assets/cat_icon.ico'  # Make sure to add an icon file
    ])
    
    # Copy assets to dist folder
    dist_assets = os.path.join(dist_dir, 'assets')
    if not os.path.exists(dist_assets):
        shutil.copytree(assets_dir, dist_assets)

if __name__ == "__main__":
    build_exe()
