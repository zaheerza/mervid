#!/usr/bin/env python3
"""
Build script to create Windows executable from video_merger_qt.py (PyQt5 version)
Run this script on Windows to create the executable.
"""

import os
import subprocess
import sys


def main():
    """Build the Windows executable using PyInstaller."""
    print("=" * 60)
    print("Video Merger (PyQt5) - Executable Builder")
    print("=" * 60)

    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Check if dependencies are installed
    try:
        import PyQt5
        print(f"PyQt5 installed")
    except ImportError:
        print("PyQt5 not found. Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    try:
        import moviepy
        print(f"MoviePy installed")
    except ImportError:
        print("MoviePy not found. Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    # PyInstaller command
    script_path = os.path.join(os.path.dirname(__file__), "video_merger_qt.py")

    pyinstaller_args = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",                    # Single executable file
        "--windowed",                   # No console window (GUI app)
        "--name", "VideoMerger",        # Executable name
        "--clean",                      # Clean cache before building
        "--noconfirm",                  # Replace output without confirmation
        # Hidden imports needed by moviepy
        "--hidden-import", "moviepy",
        "--hidden-import", "PIL",
        "--hidden-import", "PIL.Image",
        "--hidden-import", "numpy",
        "--hidden-import", "proglog",
        "--hidden-import", "imageio",
        "--hidden-import", "imageio_ffmpeg",
        "--hidden-import", "decorator",
        "--hidden-import", "tqdm",
        # PyQt5 imports
        "--hidden-import", "PyQt5",
        "--hidden-import", "PyQt5.QtCore",
        "--hidden-import", "PyQt5.QtGui",
        "--hidden-import", "PyQt5.QtWidgets",
        # Collect all data files
        "--collect-all", "moviepy",
        "--collect-all", "imageio_ffmpeg",
        script_path
    ]

    print("\nBuilding executable...")
    print("This may take a few minutes...\n")

    try:
        subprocess.check_call(pyinstaller_args)
        print("\n" + "=" * 60)
        print("BUILD SUCCESSFUL!")
        print("=" * 60)
        print("\nThe executable can be found at:")
        print("  dist/VideoMerger.exe")
        print("\nNote: The executable bundles imageio-ffmpeg which includes FFmpeg.")
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
