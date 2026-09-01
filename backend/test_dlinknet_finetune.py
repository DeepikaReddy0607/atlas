from pathlib import Path
import json
import random
import time

import numpy as np
from PIL import Image, ImageOps

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

from app.engines.vision.models.dlinknet import DLinkNet34


# ============================================================
# SMOKE TEST CONFIG
# ============================================================

SPLIT_FILE = Path(
    "generated/deepglobe_split.json"
)

BASE_CHECKPOINT = Path(
    "models/dlinknet/log01_dink34.th"
)

OUTPUT_CHECKPOINT = Path(
    "generated/dlinknet_smoke_test.pth"
)

SEED = 42

# IMPORTANT:
# This is intentionally tiny.
TRAIN_IMAGES = 20
VALIDATION_IMAGES = 10

# Resize before training.
IMAGE_SIZE = 512

EPOCHS = 1

BATCH_SIZE = 1

LEARNING_RATE = 1e-5

PRINT_EVERY = 1


# ============================================================
# REPRODUCIBILITY
# ============================================================

def seed_everything(seed):

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


# ============================================================
# DATASET
# ============================================================

class DeepGlobeSmokeDataset(Dataset):

    def __init__(
        self,
        pairs,
        augment=False,
    ):

        self.pairs = pairs
        self.augment = augment

        self.mean = np.array(
            [0.485, 0.456, 0.406],
            dtype=np.float32,
        )

        self.std = np.array(
            [0.229, 0.224, 0.225],
            dtype=np.float32,
        )

    def __len__(self):

        return len(self.pairs)

    def __getitem__(
        self,
        index,
    ):

        item = self.pairs[index]

        image = Image.open(
            item["image"]
        ).convert("RGB")

        mask = Image.open(
            item["mask"]
        ).convert("L")

        # ----------------------------------------------------
        # Resize
        # ----------------------------------------------------

        image = image.resize(
            (IMAGE_SIZE, IMAGE_SIZE),
            Image.Resampling.BILINEAR,
        )

        mask = mask.resize(
            (IMAGE_SIZE, IMAGE_SIZE),
            Image.Resampling.NEAREST,
        )

        # ----------------------------------------------------
        # Simple spatial augmentation
        # ----------------------------------------------------

        if self.augment:

            if random.random() < 0.5:

                image = ImageOps.mirror(
                    image
                )

                mask = ImageOps.mirror(
                    mask
                )

            if random.random() < 0.5:

                image = ImageOps.flip(
                    image
                )

                mask = ImageOps.flip(
                    mask
                )

        # ----------------------------------------------------
        # Image tensor
        # ----------------------------------------------------

        image_array = (
            np.asarray(
                image,
                dtype=np.float32,
            )
            / 255.0
        )

        image_array = (
            image_array - self.mean
        ) / self.std

        image_tensor = torch.from_numpy(
            image_array
        ).permute(
            2, 0, 1
        ).float()

        # ----------------------------------------------------
        # Binary road mask
        # ----------------------------------------------------

        mask_array = (
            np.asarray(
                mask,
                dtype=np.uint8,
            )
            > 127
        ).astype(
            np.float32
        )

        mask_tensor = torch.from_numpy(
            mask_array
        ).unsqueeze(
            0
        ).float()

        return (
            image_tensor,
            mask_tensor,
        )


# ============================================================
# DICE LOSS
# ============================================================

def dice_loss(
    logits,
    targets,
):

    probabilities = torch.sigmoid(
        logits
    )

    probabilities = probabilities.reshape(
        probabilities.shape[0],
        -1,
    )

    targets = targets.reshape(
        targets.shape[0],
        -1,
    )

    intersection = (
        probabilities * targets
    ).sum(
        dim=1
    )

    denominator = (
        probabilities.sum(dim=1)
        +
        targets.sum(dim=1)
    )

    dice = (
        (2.0 * intersection + 1.0)
        /
        (denominator + 1.0)
    )

    return 1.0 - dice.mean()


# ============================================================
# LOSS
# ============================================================

def loss_function(
    logits,
    targets,
):

    bce = nn.functional.binary_cross_entropy_with_logits(
        logits,
        targets,
    )

    dice = dice_loss(
        logits,
        targets,
    )

    return (
        0.5 * bce
        +
        0.5 * dice
    )


# ============================================================
# METRICS
# ============================================================

def metrics(
    logits,
    targets,
):

    probabilities = torch.sigmoid(
        logits
    )

    predictions = (
        probabilities >= 0.5
    )

    targets = (
        targets >= 0.5
    )

    tp = (
        predictions & targets
    ).sum().item()

    fp = (
        predictions & ~targets
    ).sum().item()

    fn = (
        ~predictions & targets
    ).sum().item()

    union = (
        tp + fp + fn
    )

    iou = (
        tp / union
        if union > 0
        else 1.0
    )

    dice_denominator = (
        2 * tp + fp + fn
    )

    dice = (
        2 * tp / dice_denominator
        if dice_denominator > 0
        else 1.0
    )

    return iou, dice


# ============================================================
# LOAD BASE CHECKPOINT
# ============================================================

def load_checkpoint(
    model,
):

    print()
    print(
        "Loading D-LinkNet checkpoint..."
    )

    checkpoint = torch.load(
        BASE_CHECKPOINT,
        map_location="cpu",
    )

    if (
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

        if key.startswith(
            "module."
        ):

            key = key[7:]

        cleaned[key] = value

    model.load_state_dict(
        cleaned,
        strict=True,
    )

    print(
        "Checkpoint loaded successfully."
    )


# ============================================================
# VALIDATION
# ============================================================

def validate(
    model,
    loader,
    device,
):

    model.eval()

    total_iou = 0.0
    total_dice = 0.0

    with torch.no_grad():

        for (
            images,
            masks,
        ) in loader:

            images = images.to(
                device
            )

            masks = masks.to(
                device
            )

            logits = model(
                images
            )

            iou, dice = metrics(
                logits,
                masks,
            )

            total_iou += iou
            total_dice += dice

    count = len(loader)

    return (
        total_iou / count,
        total_dice / count,
    )


# ============================================================
# MAIN
# ============================================================

def main():

    seed_everything(
        SEED
    )

    print("=" * 70)
    print(
        "ATLAS — D-LINKNET FINE-TUNING SMOKE TEST"
    )
    print("=" * 70)

    # --------------------------------------------------------
    # Device
    # --------------------------------------------------------

    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    print(
        f"Device: {device}"
    )

    if device.type == "cpu":

        print(
            "CPU mode: smoke test only."
        )

    # --------------------------------------------------------
    # Split
    # --------------------------------------------------------

    with open(
        SPLIT_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        split = json.load(
            file
        )

    train_pairs = split[
        "train"
    ][:TRAIN_IMAGES]

    validation_pairs = split[
        "validation"
    ][:VALIDATION_IMAGES]

    print()
    print(
        "SMOKE TEST DATA"
    )

    print(
        f"Training   : "
        f"{len(train_pairs)} images"
    )

    print(
        f"Validation : "
        f"{len(validation_pairs)} images"
    )

    print(
        f"Resolution : "
        f"{IMAGE_SIZE}x{IMAGE_SIZE}"
    )

    print(
        f"Epochs     : "
        f"{EPOCHS}"
    )

    # --------------------------------------------------------
    # Dataset
    # --------------------------------------------------------

    train_dataset = (
        DeepGlobeSmokeDataset(
            train_pairs,
            augment=True,
        )
    )

    validation_dataset = (
        DeepGlobeSmokeDataset(
            validation_pairs,
            augment=False,
        )
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0,
    )

    validation_loader = DataLoader(
        validation_dataset,
        batch_size=1,
        shuffle=False,
        num_workers=0,
    )

    # --------------------------------------------------------
    # Model
    # --------------------------------------------------------

    print()
    print(
        "Building D-LinkNet34..."
    )

    model = DLinkNet34(
        num_classes=1,
        pretrained_encoder=False,
    )

    load_checkpoint(
        model
    )

    model.to(
        device
    )

    # --------------------------------------------------------
    # Baseline validation
    # --------------------------------------------------------

    print()
    print(
        "BASELINE VALIDATION"
    )

    baseline_iou, baseline_dice = (
        validate(
            model,
            validation_loader,
            device,
        )
    )

    print(
        f"Baseline IoU  : "
        f"{baseline_iou:.4f}"
    )

    print(
        f"Baseline Dice : "
        f"{baseline_dice:.4f}"
    )

    # --------------------------------------------------------
    # Optimizer
    # --------------------------------------------------------

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=1e-4,
    )

    # --------------------------------------------------------
    # Training
    # --------------------------------------------------------

    print()
    print(
        "TRAINING"
    )

    for epoch in range(
        1,
        EPOCHS + 1,
    ):

        model.train()

        epoch_loss = 0.0

        epoch_start = (
            time.perf_counter()
        )

        for step, (
            images,
            masks,
        ) in enumerate(
            train_loader,
            start=1,
        ):

            step_start = (
                time.perf_counter()
            )

            images = images.to(
                device
            )

            masks = masks.to(
                device
            )

            optimizer.zero_grad()

            logits = model(
                images
            )

            loss = loss_function(
                logits,
                masks,
            )

            loss.backward()

            optimizer.step()

            epoch_loss += (
                loss.item()
            )

            elapsed = (
                time.perf_counter()
                - step_start
            )

            print(
                f"[Epoch "
                f"{epoch}/{EPOCHS}] "
                f"[Batch "
                f"{step}/{len(train_loader)}] "
                f"Loss: "
                f"{loss.item():.5f} "
                f"Time: "
                f"{elapsed:.2f}s"
            )

        epoch_time = (
            time.perf_counter()
            - epoch_start
        )

        # ----------------------------------------------------
        # Validation
        # ----------------------------------------------------

        val_iou, val_dice = (
            validate(
                model,
                validation_loader,
                device,
            )
        )

        average_loss = (
            epoch_loss
            / len(train_loader)
        )

        print()
        print(
            "=" * 70
        )

        print(
            f"EPOCH {epoch} COMPLETE"
        )

        print(
            f"Training loss : "
            f"{average_loss:.5f}"
        )

        print(
            f"Validation IoU: "
            f"{val_iou:.4f}"
        )

        print(
            f"Validation Dice: "
            f"{val_dice:.4f}"
        )

        print(
            f"Epoch time    : "
            f"{epoch_time:.2f}s"
        )

        print(
            "=" * 70
        )

    # --------------------------------------------------------
    # Save smoke-test checkpoint
    # --------------------------------------------------------

    torch.save(
        model.state_dict(),
        OUTPUT_CHECKPOINT,
    )

    print()
    print(
        "SMOKE TEST COMPLETE"
    )

    print(
        f"Baseline IoU : "
        f"{baseline_iou:.4f}"
    )

    print(
        f"After train  : "
        f"{val_iou:.4f}"
    )

    print(
        f"Change       : "
        f"{val_iou - baseline_iou:+.4f}"
    )

    print(
        f"Checkpoint   : "
        f"{OUTPUT_CHECKPOINT}"
    )

    if val_iou > baseline_iou:

        print()
        print(
            "RESULT: TRAINING SHOWS POSITIVE "
            "VALIDATION MOVEMENT."
        )

    else:

        print()
        print(
            "RESULT: NO POSITIVE VALIDATION "
            "MOVEMENT YET."
        )

    print()
    print(
        "DO NOT SCALE TRAINING YET."
    )

    print(
        "Evaluate this smoke test first."
    )


if __name__ == "__main__":
    main()