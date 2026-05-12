import subprocess
import shutil
from pathlib import Path
from src.utils.file_scanner import EXTENSIONES_IMAGEN, EXTENSIONES_VIDEO

THUMB_W = 320
THUMB_H = 200


def ruta_thumbnail(ruta_archivo, carpeta_thumbs='thumbnails'):
    p = Path(ruta_archivo)
    nombre = f"{p.stem}_{p.suffix.lstrip('.')}.jpg"
    return str(Path(carpeta_thumbs).resolve() / nombre)


def thumbnail_existe(ruta_archivo, carpeta_thumbs='thumbnails'):
    return Path(ruta_thumbnail(ruta_archivo, carpeta_thumbs)).exists()


def generar_thumbnail(ruta_archivo, carpeta_thumbs='thumbnails'):
    """Genera thumbnail; retorna la ruta o None si falla."""
    ext = Path(ruta_archivo).suffix.lower()
    Path(carpeta_thumbs).mkdir(parents=True, exist_ok=True)
    if ext in EXTENSIONES_IMAGEN:
        return _thumb_imagen(ruta_archivo, carpeta_thumbs)
    if ext in EXTENSIONES_VIDEO:
        return _thumb_video(ruta_archivo, carpeta_thumbs)
    return None


def _thumb_imagen(ruta, carpeta_thumbs):
    try:
        from PIL import Image
        dest = ruta_thumbnail(ruta, carpeta_thumbs)
        img = Image.open(ruta).convert('RGB')
        img.thumbnail((THUMB_W, THUMB_H), Image.LANCZOS)
        img.save(dest, 'JPEG', quality=85)
        return dest
    except Exception:
        return None


def _thumb_video(ruta, carpeta_thumbs):
    if not shutil.which('ffmpeg'):
        return None
    dest = ruta_thumbnail(ruta, carpeta_thumbs)
    try:
        subprocess.run(
            [
                'ffmpeg', '-y', '-i', ruta,
                '-ss', '00:00:01', '-vframes', '1',
                '-vf', (
                    f'scale={THUMB_W}:{THUMB_H}:force_original_aspect_ratio=decrease,'
                    f'pad={THUMB_W}:{THUMB_H}:(ow-iw)/2:(oh-ih)/2'
                ),
                dest,
            ],
            capture_output=True,
            timeout=15,
        )
    except Exception:
        return None
    return dest if Path(dest).exists() else None
