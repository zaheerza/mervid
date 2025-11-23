# Video Merger

A simple GUI application to merge multiple video clips into one video file.

## Features

- Drag and drop multiple video files
- Reorder videos before merging
- Support for common video formats: MP4, AVI, MOV, MKV, WMV, FLV, WebM, MPEG
- Resolution options: Original, 720p, or 1080p
- Progress indicator during merge
- Easy-to-use graphical interface

## Installation

### Option 1: Run from Source

1. Install Python 3.8 or higher from [python.org](https://www.python.org/downloads/)

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python video_merger.py
   ```

### Option 2: Create Windows Executable

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the build script:
   ```bash
   python build_executable.py
   ```

3. Find the executable at `dist/VideoMerger.exe`

### Manual PyInstaller Build

If you prefer to build manually, run:
```bash
pyinstaller --onefile --windowed --name VideoMerger video_merger.py
```

## Usage

1. **Add Videos**: Click "Add Videos" to select video files to merge
2. **Reorder**: Use "Move Up" and "Move Down" to arrange the order
3. **Output Settings**:
   - Click "Browse..." to choose where to save the merged video
   - Select resolution (Original, 720p, or 1080p)
4. **Merge**: Click "Merge Videos" to start the process

## Supported Formats

### Input Formats
- MP4 (.mp4)
- AVI (.avi)
- MOV (.mov)
- MKV (.mkv)
- WMV (.wmv)
- FLV (.flv)
- WebM (.webm)
- MPEG (.mpeg, .mpg)
- M4V (.m4v)

### Output Formats
- MP4 (recommended)
- AVI
- MOV
- MKV

## Requirements

- Python 3.8+
- moviepy
- pillow
- numpy
- FFmpeg (bundled with imageio-ffmpeg)

## Troubleshooting

### "moviepy not found" error
Run: `pip install moviepy`

### Videos not merging correctly
- Ensure all videos have the same frame rate for best results
- Try selecting a specific resolution (720p or 1080p) to normalize all clips

### Executable won't start
- Make sure you have Windows 10/11
- Try running as Administrator
- Check if Windows Defender is blocking the application

## License

MIT License - Free to use and modify.
