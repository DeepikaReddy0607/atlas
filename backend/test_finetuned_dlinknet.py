from pathlib import Path
import json
import random
import time

import numpy as np
from PIL import Image

import torch

from app.engines.vision.models.dlinknet import DLinkNet34


# ============================================================
# CONFIG
# ============================================================

SPLIT_FILE = Path(
    "generated/deepglobe_split.json"
)

CHECKPOINT = Path(
    "models/dlinknet/finetuned_500/"
    "dlinknet34_deepglobe_500_best.pth"
)

IMAGE_SIZE = 512

VALIDATION_COUNT = 100

THRESHOLD = 0.5

SEED = 42


# ============================================================
# DATASET
# ============================================================

class Dataset:

    def __init__(self, pairs):

        self.pairs = pairs

        self.mean = np.array(
            [0.485, 0.456, 0.406],
            dtype=np.float32,
        )

        self.std = np.array(
            [0.229, 0.224, 0.225],
            dtype=np.float32,
        )

    def load(self, item):

        image = Image.open(
            item["image"]
        ).convert("RGB")

        mask = Image.open(
            item["mask"]
        ).convert("L")

        image = image.resize(
            (IMAGE_SIZE, IMAGE_SIZE),
            Image.Resampling.BILINEAR,
        )

        mask = mask.resize(
            (IMAGE_SIZE, IMAGE_SIZE),
            Image.Resampling.NEAREST,
        )

        image = (
            np.asarray(
                image,
                dtype=np.float32,
            ) / 255.0
        )

        image = (
            image - self.mean
        ) / self.std

        image = torch.from_numpy(
            image
        ).permute(
            2, 0, 1
        ).float()

        mask = (
            np.asarray(
                mask,
                dtype=np.uint8,
            ) > 127
        ).astype(
            np.uint8
        )

        return image, mask


# ============================================================
# CHECKPOINT LOADING
# ============================================================

def load_model(device):

    print()
    print(
        "Loading fine-tuned D-LinkNet34..."
    )

    model = DLinkNet34(
        num_classes=1,
        pretrained_encoder=False,
    )

    checkpoint = torch.load(
        CHECKPOINT,
        map_location="cpu",
    )

    if (
        isinstance(checkpoint, dict)
        and "model_state_dict" in checkpoint
    ):

        state_dict = checkpoint[
            "model_state_dict"
        ]

    elif (
        isinstance(checkpoint, dict)
        and "state_dict" in checkpoint
    ):

        state_dict = checkpoint[
            "state_dict"
        ]

    else:

        state_dict = checkpoint

    cleaned = {}

    for key, value in state_dict.items():

        if key.startswith("module."):
            key = key[7:]

        cleaned[key] = value

    model.load_state_dict(
        cleaned,
        strict=True,
    )

    model.to(device)
    model.eval()

    print(
        "Fine-tuned checkpoint loaded."
    )

    return model


# ============================================================
# EVALUATION
# ============================================================

def evaluate(
    model,
    dataset,
    device,
):

    tp = 0
    fp = 0
    fn = 0
    tn = 0

    inference_times = []

    total = len(dataset.pairs)

    with torch.no_grad():

        for index, item in enumerate(
            dataset.pairs,
            start=1,
        ):

            image, target = dataset.load(
                item
            )

            image = image.unsqueeze(
                0
            ).to(device)

            start = time.perf_counter()

            logits = model(
                image
            )

            elapsed = (
                time.perf_counter()
                - start
            ) * 1000

            inference_times.append(
                elapsed
            )

            probability = torch.sigmoid(
                logits
            )

            prediction = (
                probability[0, 0]
                .cpu()
                .numpy()
                >= THRESHOLD
            )

            target = target.astype(
                bool
            )

            tp += int(
                np.logical_and(
                    prediction,
                    target,
                ).sum()
            )

            fp += int(
                np.logical_and(
                    prediction,
                    ~target,
                ).sum()
            )

            fn += int(
                np.logical_and(
                    ~prediction,
                    target,
                ).sum()
            )

            tn += int(
                np.logical_and(
                    ~prediction,
                    ~target,
                ).sum()
            )

            print(
                f"[{index}/{total}] "
                f"{Path(item['image']).name}"
            )

    union = tp + fp + fn

    iou = (
        tp / union
        if union
        else 0.0
    )

    dice_denominator = (
        2 * tp + fp + fn
    )

    dice = (
        2 * tp / dice_denominator
        if dice_denominator
        else 0.0
    )

    precision = (
        tp / (tp + fp)
        if tp + fp
        else 0.0
    )

    recall = (
        tp / (tp + fn)
        if tp + fn
        else 0.0
    )

    accuracy = (
        (tp + tn)
        /
        (tp + tn + fp + fn)
    )

    return {
        "iou": iou,
        "dice": dice,
        "precision": precision,
        "recall": recall,
        "accuracy": accuracy,
        "inference_ms":
            float(
                np.mean(
                    inference_times
                )
            ),
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print(
        "ATLAS — FINE-TUNED D-LINKNET EVALUATION"
    )
    print("=" * 70)

    if not CHECKPOINT.exists():

        raise FileNotFoundError(
            f"Checkpoint not found:\n"
            f"{CHECKPOINT}"
        )

    with open(
        SPLIT_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        split = json.load(file)

    rng = np.random.default_rng(
        SEED + 1
    )

    indices = rng.choice(
        len(split["validation"]),
        size=min(
            VALIDATION_COUNT,
            len(split["validation"]),
        ),
        replace=False,
    )

    indices.sort()

    pairs = [
        split["validation"][i]
        for i in indices
    ]

    print()
    print(
        f"Validation images : "
        f"{len(pairs)}"
    )

    print(
        f"Resolution         : "
        f"{IMAGE_SIZE}x{IMAGE_SIZE}"
    )

    print(
        f"Threshold          : "
        f"{THRESHOLD}"
    )

    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    print(
        f"Device             : "
        f"{device}"
    )

    model = load_model(
        device
    )

    dataset = Dataset(
        pairs
    )

    print()
    print(
        "EVALUATION START"
    )
    print(
        "-" * 70
    )

    result = evaluate(
        model,
        dataset,
        device,
    )

    print()
    print("=" * 70)
    print(
        "FINE-TUNED D-LINKNET RESULT"
    )
    print("=" * 70)

    print(
        f"IoU       : "
        f"{result['iou']:.4f}"
    )

    print(
        f"Dice      : "
        f"{result['dice']:.4f}"
    )

    print(
        f"Precision : "
        f"{result['precision']:.4f}"
    )

    print(
        f"Recall    : "
        f"{result['recall']:.4f}"
    )

    print(
        f"Accuracy  : "
        f"{result['accuracy']:.4f}"
    )

    print(
        f"Inference : "
        f"{result['inference_ms']:.2f} ms"
    )

    print()
    print(
        "REFERENCE RESULTS"
    )
    print(
        "-" * 70
    )

    print(
        "Original D-LinkNet : 0.4891 IoU"
    )

    print(
        "Best ensemble      : 0.4998 IoU"
    )

    print()

    if result["iou"] > 0.4998:

        print(
            "RESULT: NEW MODEL BEATS "
            "THE CURRENT ENSEMBLE."
        )

    elif result["iou"] > 0.4891:

        print(
            "RESULT: FINE-TUNED D-LINKNET "
            "BEATS ORIGINAL D-LINKNET, "
            "BUT NOT THE ENSEMBLE."
        )

    else:

        print(
            "RESULT: FINE-TUNING DOES NOT "
            "BEAT THE CURRENT BASELINES."
        )

    print("=" * 70)


if __name__ == "__main__":
    main()