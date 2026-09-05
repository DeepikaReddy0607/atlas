from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent

GENERATED_DIR = BASE_DIR / "generated"

CHECKPOINT_DIR = BASE_DIR / "models"

DEFAULT_MODEL = "ade20k"