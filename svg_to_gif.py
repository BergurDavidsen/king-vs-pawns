import subprocess
import os

def create_gif(png_dir, output_path):
    cmd = [
        "ffmpeg",
        "-y",
        "-framerate", "2",
        "-i", os.path.join(png_dir, "frame_%03d.png"),
        "-vf", "scale=512:-1",
        output_path
    ]
    subprocess.run(cmd)