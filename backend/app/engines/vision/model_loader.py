from pathlib import Path


class ModelLoader:

    CHECKPOINT_DIR = Path("checkpoints")

    @classmethod
    def get_checkpoint(cls, model_name: str) -> Path:

        model_dir = cls.CHECKPOINT_DIR / model_name

        if not model_dir.exists():
            raise FileNotFoundError(
                f"Checkpoint directory not found: {model_dir}"
            )

        return model_dir