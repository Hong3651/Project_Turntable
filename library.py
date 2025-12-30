from pathlib import Path
from typing import List

SUPPORTED = {".mp3"}

def scan_mp3(music_dir: str) -> List[str]:
    p = Path(music_dir).expanduser()
    if not p.exists():
        raise FileNotFoundError(f"Music directory not found: {p}")

    tracks = [str(f) for f in p.rglob("*") if f.is_file() and f.suffix.lower() in SUPPORTED]
    if not tracks:
        raise ValueError(f"No mp3 files found under: {p}")
    return tracks
