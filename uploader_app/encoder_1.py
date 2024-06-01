import subprocess
import os
import sys
from slugify import slugify
from django.conf import settings

def encode_and_segment_video(input_file, output_dir):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Encode and segment the video using DASH in one step
    encode_segment_command = [
        'ffmpeg', '-i', input_file,
        '-vf', 'scale=1920:1080',
        '-c:v', 'libx264', '-c:a', 'aac',
        '-b:v', '5000k', '-b:a', '192k',
        '-f', 'dash',
        '-min_seg_duration', '2000000',
        '-use_template', '1',
        '-use_timeline', '1',
        '-init_seg_name', 'init.mp4',
        '-media_seg_name', 'chunk_$Number$.m4s',
        os.path.join(output_dir, 'manifest.mpd')
    ]
    subprocess.run(encode_segment_command, check=True)

def encode(input_file):
    # if len(sys.argv) != 2:
    #     print("Usage: python encoder.py <input_file>")
    #     sys.exit(1)

    # input_file = sys.argv[1]
    # supported_formats = ['.mp4', '.mov', '.mkv', '.flv']
    
    # if not any(input_file.lower().endswith(ext) for ext in supported_formats):
    #     print("Unsupported file format. Supported formats are: mp4, mov, mkv, flv")
    #     sys.exit(1)

    output_dir = 'dash_output_' + slugify(os.path.basename(input_file)[:-4])
    
    print("Encoding and segmenting video...")
    encode_and_segment_video(input_file, output_dir)
    
    print("DASH packaging complete. Files are located in the directory:", output_dir)
    

def process_video(file_path, title):

    # output_dir = os.path.join(settings.MEDIA_ROOT, 'dash_output')
    output_dir = 'dash_output_' + slugify(os.path.basename(file_path)[:-4])
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{title}.mpd")
    command = [
        'ffmpeg', '-i', file_path, '-map', '0', '-s:v', '1920x1080', '-c:v', 'libx264', '-b:v', '2400k', '-an', '-f', 'dash', output_file
    ]
    result = subprocess.run(command, capture_output=True, text=True)

    print(result.stderr)

if __name__ == '__main__':
    path = '/mnt/Video Projects/final cuts/Video.mp4'
    process_video(path, 'test')