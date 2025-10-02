# DOOM Game Video Recording Setup

## Prerequisites

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   Or manually:
   ```bash
   pip install pygame
   ```

2. **Install ffmpeg (for video conversion):**
   - **macOS**: `brew install ffmpeg`
   - **Ubuntu**: `sudo apt install ffmpeg`
   - **Windows**: Download from https://ffmpeg.org/

## Usage

### 1. Single Headless Session
```bash
python main.py
```

### 2. Multiple Headless Sessions
```bash
python headless_runner.py 5
```

### 3. Convert Frames to MP4 Videos
```bash
python create_videos.py
```

### 4. Test Recording
```bash
python test_recording.py
```

## Output Structure

```
recordings/
├── session_20241201_143022/
│   ├── frame_000001.png
│   ├── frame_000002.png
│   ├── ...
│   ├── recording_data.json
│   └── session_20241201_143022.mp4
└── session_20241201_143156/
    └── ...
```

## Recording Data Format

Each session includes `recording_data.json` with:
- All generated colors
- Visited waypoints in order
- Timestamps
- Session metadata

## Troubleshooting

### "No video mode has been set" Error
- Make sure pygame is installed: `pip install pygame`
- Environment variables are set automatically in headless mode

### "No module named 'pygame'" Error
- Install pygame: `pip install pygame`
- Or use conda: `conda install pygame`

### No recordings created
- Check that `RECORD_VIDEO = True` in `settings.py`
- Verify the `recordings/` directory is writable
- Run `python test_recording.py` to debug