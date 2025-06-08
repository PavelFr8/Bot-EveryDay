from pathlib import Path

TEXTS_DIR = Path(__file__).resolve().parent.parent / "texts"


def load_text(filename: str) -> str:
    file_path = TEXTS_DIR / filename
    return file_path.read_text(encoding="utf-8")
