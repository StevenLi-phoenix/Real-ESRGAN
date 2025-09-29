import os
from pathlib import Path
import shutil
import subprocess
import re

def get_frame_rate(video_path):
    # Run ffmpeg to get video info
    result = subprocess.run(
        ['ffmpeg', '-i', str(video_path)],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )
    output = result.stderr
    # Search for frame rate in ffmpeg output
    match = re.search(r'(\d+(?:\.\d+)?)\s*fps', output)
    if match:
        return float(match.group(1))
    else:
        print("Could not determine frame rate.")
        exit(1)

# check ffmpeg on path
if os.system('where ffmpeg >nul 2>nul') != 0:
    print('ffmpeg not found')
    exit(1)

movie_path = Path(input('Enter the path to the movie: '))
TEMP_PATH = Path('temp')
if TEMP_PATH.exists():
    shutil.rmtree(TEMP_PATH)
os.makedirs(TEMP_PATH, exist_ok=True)
if movie_path.exists():
    shutil.copy(movie_path, TEMP_PATH / 'movie.mp4')

# ffmpeg -i movie.mp4 -qscale:v 1 -qmin 1 -qmax 1 -vsync 0 temp/frame%08d.png
os.makedirs(TEMP_PATH / "temp_frames", exist_ok=True)
os.system(f'ffmpeg -i "{TEMP_PATH / "movie.mp4"}" -qscale:v 1 -qmin 1 -qmax 1 -vsync 0 "{TEMP_PATH / "temp_frames"}/frame%08d.png"')


frame_rate = get_frame_rate(TEMP_PATH / "movie.mp4")
print(f'Frame rate: {frame_rate}')

# realesrgan-ncnn-vulkan.exe -i temp -o temp/realesrgan -n realesr-animevideov3 -s 2 -f jpg
os.makedirs(TEMP_PATH / "realesrgan", exist_ok=True)
os.system(f'uv run inference_realesrgan.py -i "{TEMP_PATH / "temp_frames"}" -o "{TEMP_PATH / "realesrgan"}" -n realesr-animevideov3 -s 2 -f jpg')

# ffmpeg -r {frame_rate} -i temp/realesrgan/frame%08d.jpg -c:v av1_nvenc -rc vbr -cq 28  -b:v 0 -r {frame_rate} -pix_fmt yuv420p output.mp4
os.system(f'ffmpeg -r {frame_rate} -i "{TEMP_PATH / "realesrgan"}/frame%08d.jpg" -c:v av1_nvenc -rc vbr -cq 28  -b:v 0 -r {frame_rate} -pix_fmt yuv420p "{movie_path.stem}_realesrgan.mp4"')

# rm -rf temp
shutil.rmtree(TEMP_PATH)