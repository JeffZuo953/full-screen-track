import os
import shutil
from pathlib import Path

def build():
    # Remove old build if exists
    build_dir = Path("installer/FullScreenTrack")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # The PyInstaller output is now in dist/ScreenTrack
    dist_dir = Path("dist/ScreenTrack")
    if not dist_dir.exists():
        print(f"Error: {dist_dir} does not exist! Make sure PyInstaller completed successfully.")
        return False
        
    print(f"Copy complete! Ready for NSIS packaging.")
    return True

if __name__ == "__main__":
    if not build():
        exit(1)
