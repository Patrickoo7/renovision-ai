import uuid
from pathlib import Path
from PIL import Image

def validate_image(content_type: str, size: int, max_size: int = 10 * 1024 * 1024) -> tuple[bool, str]:
    allowed = ['image/jpeg', 'image/png', 'image/jpg']
    if content_type not in allowed:
        return False, f"Invalid file type: {content_type}. Allowed: jpg, png"
    if size > max_size:
        return False, f"File too large: {size} bytes. Max: {max_size}"
    return True, "OK"

def generate_filename(ext: str = ".jpg") -> str:
    return f"{uuid.uuid4().hex}{ext}"

def get_image_dimensions(path: str) -> tuple[int, int]:
    with Image.open(path) as img:
        return img.size  # (width, height)
