import os

from PIL import Image


def compress_image(file_path, output_path=None, quality=85):
    """压缩图片"""
    try:
        with Image.open(file_path) as img:
            if output_path is None:
                output_path = file_path
            img.save(output_path, optimize=True, quality=quality)
    except IOError:
        print("压缩图片失败", file_path)
