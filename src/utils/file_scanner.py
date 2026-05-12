from pathlib import Path

EXTENSIONES_IMAGEN = {'.png', '.jpg', '.jpeg'}
EXTENSIONES_VIDEO  = {'.mp4', '.mov', '.mkv'}


def listar_imagenes(carpeta: str) -> list:
    base = Path(carpeta).resolve()
    if not base.exists():
        return []
    return sorted([
        str(p) for p in base.iterdir()
        if p.is_file() and p.suffix.lower() in EXTENSIONES_IMAGEN
    ])


def listar_archivos_galeria(carpeta: str) -> list:
    """Retorna imágenes y videos mezclados, ordenados por nombre."""
    base = Path(carpeta).resolve()
    if not base.exists():
        return []
    extensiones = EXTENSIONES_IMAGEN | EXTENSIONES_VIDEO
    return sorted([
        str(p) for p in base.iterdir()
        if p.is_file() and p.suffix.lower() in extensiones
    ])
