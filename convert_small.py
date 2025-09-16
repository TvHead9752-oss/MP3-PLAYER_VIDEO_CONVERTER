import sys
import os
import subprocess
import re
import json
import time
import shutil
import pysubs2

# ---- CONFIG ----
OUTPUT_FOLDER = os.path.join(os.path.expanduser("~"), "Converted")
FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"  # Update if different
VIDEO_SIZE = "320x240"
VIDEO_CODEC = "mpeg1video"
VIDEO_BITRATE = "600k"
AUDIO_CODEC = "mp2"
AUDIO_RATE = "44100"
AUDIO_CHANNELS = "2"
AUDIO_BITRATE = "128k"
VIDEO_EXTENSIONS = [".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv", ".mpg"]

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ---- HELPERS ----
def find_video_files(paths):
    files = []
    for path in paths:
        if os.path.isfile(path) and os.path.splitext(path)[1].lower() in VIDEO_EXTENSIONS:
            files.append(path)
        elif os.path.isdir(path):
            for root, _, filenames in os.walk(path):
                for name in filenames:
                    if os.path.splitext(name)[1].lower() in VIDEO_EXTENSIONS:
                        files.append(os.path.join(root, name))
    return files

def get_unique_output_path(base_name):
    output_file = os.path.join(OUTPUT_FOLDER, f"{base_name}_converted.mpg")
    counter = 1
    while os.path.exists(output_file):
        output_file = os.path.join(OUTPUT_FOLDER, f"{base_name}_converted_{counter}.mpg")
        counter += 1
    return output_file

def ffmpeg_progress(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    duration = None
    time_pattern = re.compile(r'time=(\d+:\d+:\d+\.\d+)')
    def hms_to_seconds(hms):
        h, m, s = hms.split(':')
        return float(h) * 3600 + float(m) * 60 + float(s)
    start_time = time.time()
    for line in process.stdout:
        if 'Duration' in line:
            match = re.search(r'Duration: (\d+:\d+:\d+\.\d+)', line)
            if match:
                duration = hms_to_seconds(match.group(1))
        match_time = time_pattern.search(line)
        if match_time and duration:
            elapsed = hms_to_seconds(match_time.group(1))
            percent = (elapsed / duration) * 100
            eta = (time.time() - start_time) / (percent / 100) - (time.time() - start_time)
            print(f"\rProgress: {percent:5.1f}% | ETA: {int(eta)}s", end='')
    process.wait()
    print()

def choose_audio_stream(input_file):
    ffprobe_cmd = [
        FFMPEG_PATH.replace("ffmpeg.exe", "ffprobe.exe"),
        "-v", "error",
        "-select_streams", "a",
        "-show_entries", "stream=index:stream_tags=language,title",
        "-of", "json",
        input_file
    ]
    result = subprocess.run(ffprobe_cmd, capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    audio_streams = data.get("streams", [])
    if not audio_streams:
        print("⚠️ No audio streams found, defaulting to first track (0).")
        return 0
    print("\nAvailable audio tracks:")
    for i, stream in enumerate(audio_streams):
        tags = stream.get("tags", {})
        lang = tags.get("language", "unknown")
        title = tags.get("title", "")
        print(f"  [{i}] Stream index={stream['index']} | lang={lang} | title={title}")
    choice = input("Pick audio track number: ").strip()
    if choice.isdigit() and 0 <= int(choice) < len(audio_streams):
        return audio_streams[int(choice)]["index"]
    else:
        print("⚠️ Invalid choice, defaulting to first audio track.")
        return audio_streams[0]["index"]

def list_subtitle_streams(input_file):
    ffprobe_cmd = [
        FFMPEG_PATH.replace("ffmpeg.exe", "ffprobe.exe"),
        "-v", "error",
        "-select_streams", "s",
        "-show_entries", "stream=index:stream_tags=language,title",
        "-of", "json",
        input_file
    ]
    result = subprocess.run(ffprobe_cmd, capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    subs = data.get("streams", [])
    if not subs:
        print("⚠️ No subtitle streams found.")
    else:
        print("\nAvailable subtitle tracks:")
        for i, stream in enumerate(subs):
            tags = stream.get("tags", {})
            lang = tags.get("language", "unknown")
            title = tags.get("title", "")
            print(f"  [{i}] Stream index={stream['index']} | lang={lang} | title={title}")
    return subs

def choose_subtitle_stream(subs):
    choice = input("Pick subtitle track number to burn: ").strip()
    if choice.isdigit() and 0 <= int(choice) < len(subs):
        return subs[int(choice)]["index"]
    else:
        print("⚠️ Invalid choice, defaulting to first subtitle track.")
        return subs[0]["index"]

def extract_fonts(input_file, fonts_dir):
    os.makedirs(fonts_dir, exist_ok=True)

    # Probe attachments
    ffprobe_cmd = [
        FFMPEG_PATH.replace("ffmpeg.exe", "ffprobe.exe"),
        "-v", "error",
        "-select_streams", "t",
        "-show_entries", "stream=index:stream_tags=filename",
        "-of", "json",
        input_file
    ]
    result = subprocess.run(ffprobe_cmd, capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    attachments = data.get("streams", [])

    for attach in attachments:
        index = attach["index"]
        # Get filename from tags
        raw_filename = attach.get("tags", {}).get("filename", f"font_{index}")
        # Sanitize: allow alphanumerics, space, dot, underscore, dash
        filename = "".join(c for c in raw_filename if c.isalnum() or c in (' ', '.', '_', '-')).strip()
        # Ensure unique filename
        out_path = os.path.join(fonts_dir, filename)
        counter = 1
        while os.path.exists(out_path):
            name, ext = os.path.splitext(filename)
            out_path = os.path.join(fonts_dir, f"{name}_{counter}{ext}")
            counter += 1

        # Use -f data to extract raw attachment safely
        cmd = [
            FFMPEG_PATH,
            "-y",
            "-i", input_file,
            "-map", f"0:{index}",
            "-c", "copy",
            "-f", "data",
            out_path
        ]
        subprocess.run(cmd, check=True)

def extract_subtitle_to_srt(input_file, sub_index, output_srt):
    temp_sub = os.path.join(OUTPUT_FOLDER, "temp_sub.ass")
    cmd = [FFMPEG_PATH, "-y", "-i", input_file, "-map", f"0:{sub_index}", temp_sub]
    subprocess.run(cmd, check=True)
    subs = pysubs2.load(temp_sub)
    subs.save(output_srt)
    os.remove(temp_sub)
    return output_srt

def burn_subtitles(input_file, srt_file, temp_mkv, fonts_dir):
    # Escape paths for FFmpeg
    def ffmpeg_escape(path):
        # On Windows, wrap path in single quotes and double up backslashes
        return path.replace('\\', '\\\\').replace(':', '\\:').replace("'", "\\'")

    input_esc = ffmpeg_escape(input_file)
    srt_esc = ffmpeg_escape(srt_file)
    fonts_esc = ffmpeg_escape(fonts_dir)

    vf = f"subtitles='{srt_esc}':fontsdir='{fonts_esc}'"
    cmd = [
        FFMPEG_PATH,
        "-y",
        "-i", input_file,
        "-vf", vf,
        "-c:v", "libx264",
        "-c:a", "copy",
        temp_mkv
    ]
    ffmpeg_progress(cmd)

def mkv_to_mpg(temp_mkv, output_mpg):
    cmd = [
        FFMPEG_PATH, "-y", "-i", temp_mkv,
        "-s", VIDEO_SIZE,
        "-vcodec", VIDEO_CODEC,
        "-b:v", VIDEO_BITRATE,
        "-acodec", AUDIO_CODEC,
        "-ar", AUDIO_RATE,
        "-ac", AUDIO_CHANNELS,
        "-b:a", AUDIO_BITRATE,
        output_mpg
    ]
    ffmpeg_progress(cmd)

# ---- MAIN SCRIPT ----
input_paths = sys.argv[1:]
if not input_paths:
    print("Drag and drop files or folders onto this script to convert them.")
    input("Press Enter to exit...")
    sys.exit(0)

video_files = find_video_files(input_paths)
if not video_files:
    print("No supported video files found.")
    input("Press Enter to exit...")
    sys.exit(0)

print(f"Found {len(video_files)} file(s) to convert.\n")

for idx, input_file in enumerate(video_files, 1):
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_file = get_unique_output_path(base_name)
    chosen_audio = choose_audio_stream(input_file)
    subs = list_subtitle_streams(input_file)

    if subs:
        chosen_sub = choose_subtitle_stream(subs)
        fonts_dir = os.path.join(OUTPUT_FOLDER, f"{base_name}_fonts")
        extract_fonts(input_file, fonts_dir)

        srt_file = os.path.join(OUTPUT_FOLDER, f"{base_name}.srt")
        extract_subtitle_to_srt(input_file, chosen_sub, srt_file)

        temp_mkv = os.path.join(OUTPUT_FOLDER, f"{base_name}_temp.mkv")
        print(f"[{idx}/{len(video_files)}] Burning subtitles to temp MKV...")
        burn_subtitles(input_file, srt_file, temp_mkv, fonts_dir)

        print(f"[{idx}/{len(video_files)}] Converting temp MKV to MPG...")
        mkv_to_mpg(temp_mkv, output_file)

        # Cleanup temp files
        os.remove(temp_mkv)
        shutil.rmtree(fonts_dir, ignore_errors=True)
        print(f"✅ Done: {output_file}\n")
    else:
        # No subtitles
        cmd = [
            FFMPEG_PATH, "-y", "-i", input_file,
            "-map", f"0:v:0", "-map", f"0:a:{chosen_audio}",
            "-s", VIDEO_SIZE, "-vcodec", VIDEO_CODEC,
            "-b:v", VIDEO_BITRATE,
            "-acodec", AUDIO_CODEC,
            "-ar", AUDIO_RATE,
            "-ac", AUDIO_CHANNELS,
            "-b:a", AUDIO_BITRATE,
            output_file
        ]
        print(f"[{idx}/{len(video_files)}] Converting without subtitles...")
        ffmpeg_progress(cmd)
        print(f"✅ Done: {output_file}\n")

print("All conversions finished!")
input("Press Enter to exit...")
