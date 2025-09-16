# MP3-PLAYER_VIDEO_CONVERTER

This program takes any MKV or MP4, burns subtitles into it, and converts it into a smaller MPG that a HIFI Walker H2 with Rockbox installed can read and watch with subs!


# Video Converter Script

This Python script converts video files to **MPG format** with a specific resolution, codec, and bitrate. It supports burning subtitles and extracting embedded fonts automatically. Works with multiple video files or entire folders.

---

## **Requirements**

* Python 3.x
* [pysubs2](https://pypi.org/project/pysubs2/) (`pip install pysubs2`)
* [FFmpeg](https://ffmpeg.org/download.html) installed (update `FFMPEG_PATH` in the script if needed)

---

## **Supported Video Formats**

* `.mp4`, `.mkv`, `.avi`, `.mov`, `.flv`, `.wmv`, `.mpg`

---

## **Usage**

### **Option 1: Drag-and-drop files/folders**

* Drag one or more video files, or entire folders, onto the script file (`.py`).
* The script will automatically detect all supported videos in the folder(s).

### **Option 2: Command line**

```bash
python convert_small.py "C:\path\to\video_or_folder"
```

* Multiple paths can be provided:

```bash
python convert_small.py "C:\Videos\Movie1.mkv" "C:\Videos\Folder"
```

---

## **How It Works**

1. **Video detection**: Recursively scans folders for supported video files.
2. **Audio selection**: Prompts you to pick the audio track if multiple tracks exist.
3. **Subtitle handling**:

   * Lists available subtitle streams.
   * Prompts you to pick one for burning into the video.
   * Extracts any embedded fonts automatically.
4. **Conversion**:

   * Burns subtitles to a temporary MKV file (if selected).
   * Converts video to MPG format with the specified size, codec, and bitrate.
   * Cleans up temporary files automatically.
5. **Output**: Converted videos are saved in the `Converted` folder in your user directory.

   * Example: `C:\Users\<Username>\Converted\Movie1_converted.mpg`

---

## **Configuration**

You can adjust conversion settings by modifying the top of the script:

```python
OUTPUT_FOLDER = os.path.join(os.path.expanduser("~"), "Converted")
FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"
VIDEO_SIZE = "320x240"
VIDEO_CODEC = "mpeg1video"
VIDEO_BITRATE = "600k"
AUDIO_CODEC = "mp2"
AUDIO_RATE = "44100"
AUDIO_CHANNELS = "2"
AUDIO_BITRATE = "128k"
```

* `VIDEO_SIZE`: Output resolution (e.g., `640x480`).
* `VIDEO_CODEC`: Video codec (`mpeg1video` by default).
* `AUDIO_CODEC`, `AUDIO_RATE`, `AUDIO_CHANNELS`, `AUDIO_BITRATE`: Control audio encoding.

---

## **Example Run**

Suppose you have:

```
Videos/
├── Movie1.mkv
└── Movie2.mp4
```

Run the script:

```bash
python convert_small.py "C:\Users\Blake\Videos"
```

The script will:

1. Detect both movies.
2. Ask you to select audio and subtitle streams if available.
3. Convert each video to MPG in `C:\Users\Blake\Converted`.
4. Print progress and completion messages.

---

## **Notes**

* If a video has **no subtitles**, it will still convert without errors.
* Temporary files and fonts extracted for subtitle burning are automatically removed after conversion.
* Output filenames are made unique automatically to avoid overwriting.

