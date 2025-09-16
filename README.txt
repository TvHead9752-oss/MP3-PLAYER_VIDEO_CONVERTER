==============================
VIDEO CONVERTER PROGRAM
==============================

DESCRIPTION:
------------
This program converts video files to a smaller format (320x240, MPEG-1 video + MP2 stereo audio)
and automatically selects the best English audio track (preferring 5.1 channels if available). 
It supports multiple files and folders, and outputs all converted files to your "Converted" folder.

REQUIREMENTS:
-------------
1. Python 3 installed and added to your system PATH.
   To check, open PowerShell and run:
       python --version
2. FFmpeg installed (includes ffprobe). The default script path is:
       C:\ffmpeg\bin\ffmpeg.exe
   If your path is different, update the FFMPEG_PATH variable in the script.
3. Your video files must be in one of these formats: .mp4, .mkv, .avi, .mov, .flv, .wmv, .mpg

SETUP:
------
1. Create a folder for the program, for example:
       C:\Users\<YourName>\VideoConverter
2. Save the script file as:
       convert_small.py
3. Save this README.txt in the same folder for reference.
4. Make sure your videos are accessible on your computer.

USAGE:
------
Option A: Drag-and-Drop
1. Open File Explorer and navigate to your VideoConverter folder.
2. Select video files or folders you want to convert.
3. Drag and drop them onto the convert_small.py script.
4. Conversion will start automatically.
5. Converted files will be saved to:
       C:\Users\<YourName>\Converted

Option B: Run from Terminal
1. Open PowerShell or Command Prompt.
2. Navigate to the folder where the script is saved:
       cd "C:\Users\<YourName>\VideoConverter"
3. Run the script with files or folders as arguments:
       python convert_small.py "C:\path\to\video1.mkv" "C:\path\to\folder\with\videos"
4. Converted files will appear in the Converted folder.

NOTES:
------
- The program automatically avoids overwriting files by adding a numeric suffix.
- If a video has no English audio, the program will use the first audio track and warn you.
- Real-time progress, percentage, and estimated time remaining are displayed in the terminal.

TROUBLESHOOTING:
----------------
- If you get a "Python not found" error, make sure Python is installed and added to PATH.
- If FFmpeg cannot be found, check the FFMPEG_PATH in the script and update it.
- Ensure video files are not currently opened in another program during conversion.

ENJOY!
------
Your converted videos will now be smaller, playable, and with English audio only.
