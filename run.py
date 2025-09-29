import os
from pathlib import Path
import shutil

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

# realesrgan-ncnn-vulkan.exe -i temp -o temp/realesrgan -n realesr-animevideov3 -s 2 -f jpg
os.makedirs(TEMP_PATH / "realesrgan", exist_ok=True)
os.system(f'uv run inference_realesrgan.py -i "{TEMP_PATH / "temp_frames"}" -o "{TEMP_PATH / "realesrgan"}" -n realesr-animevideov3 -s 2 -f jpg')

# ffmpeg -r 23.98 -i temp/realesrgan/frame%08d.jpg -c:v libx264 -r 23.98 -pix_fmt yuv420p output.mp4
os.system(f'ffmpeg -r 23.98 -i "{TEMP_PATH / "realesrgan"}/frame%08d.jpg" -c:v libx264 -r 23.98 -pix_fmt yuv420p "{movie_path.stem}_realesrgan.mp4"')

# rm -rf temp
shutil.rmtree(TEMP_PATH)