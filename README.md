# Video Merger

A simple GUI application to merge multiple video clips into one video file.

**Three versions available:**
- **Streamlit version** (`video_merger_streamlit.py`) - **⭐ Recommended** - Web-based, works on all platforms
- **PyQt5 version** (`video_merger_qt.py`) - Desktop app, great for macOS
- **Tkinter version** (`video_merger.py`) - Desktop app, uses built-in Python GUI library

## Features

- Drag and drop multiple video files
- Reorder videos before merging
- Support for common video formats: MP4, AVI, MOV, MKV, WMV, FLV, WebM, MPEG
- Resolution options: Original, 720p, or 1080p
- Progress indicator during merge
- Easy-to-use graphical interface

## Installation

### Option 1: Run Streamlit Web Version (⭐ Recommended)

1. Install Python 3.8 or higher from [python.org](https://www.python.org/downloads/)

2. Install dependencies:
   ```bash
   pip install streamlit moviepy pillow numpy
   ```

3. Run the web application:
   ```bash
   streamlit run video_merger_streamlit.py
   ```

4. Your browser will open automatically at `http://localhost:8501`

**Features:**
- 🌐 Web-based - Access from any browser
- 📱 Works on all platforms (Windows, Mac, Linux)
- ☁️ Can be deployed to cloud (Streamlit Cloud, Heroku, etc.)
- 🎨 Modern, responsive UI

### Option 2: Run from Source (PyQt5 Desktop)

1. Install Python 3.8 or higher from [python.org](https://www.python.org/downloads/)

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python video_merger_qt.py
   ```

### Option 2: Run from Source (Tkinter)

1. Install Python 3.8 or higher

2. Install dependencies:
   ```bash
   pip install moviepy pillow numpy
   ```

3. Run the application:
   ```bash
   python video_merger.py
   ```

**Note for macOS users:** If you see a blank window with the Tkinter version, use the PyQt5 version instead (`video_merger_qt.py`).

### Create Windows Executable

**PyQt5 version (recommended):**
```bash
pip install -r requirements.txt
python build_executable_qt.py
```

**Tkinter version:**
```bash
pip install -r requirements.txt
python build_executable.py
```

Find the executable at `dist/VideoMerger.exe`

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

**For Streamlit version:**
- Python 3.8+
- streamlit
- moviepy
- pillow
- numpy
- FFmpeg (bundled with imageio-ffmpeg)

**For PyQt5 version:**
- Python 3.8+
- PyQt5
- moviepy
- pillow
- numpy
- FFmpeg (bundled with imageio-ffmpeg)

**For Tkinter version:**
- Python 3.8+
- moviepy
- pillow
- numpy
- FFmpeg (bundled with imageio-ffmpeg)
- tkinter (usually included with Python)

## Troubleshooting

### Blank window on macOS (Tkinter version)
The system Tk on macOS is deprecated and has rendering issues. **Solution:**
- Use the PyQt5 version instead: `python video_merger_qt.py`
- Or install PyQt5: `pip install PyQt5`

### "moviepy not found" error
Run: `pip install moviepy`

### Videos not merging correctly
- Ensure all videos have the same frame rate for best results
- Try selecting a specific resolution (720p or 1080p) to normalize all clips

### Executable won't start (Windows)
- Make sure you have Windows 10/11
- Try running as Administrator
- Check if Windows Defender is blocking the application

## License

MIT License - Free to use and modify.
