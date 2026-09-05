from pathlib import Path
import json
import random
import time

import numpy as np
from PIL import Image, ImageOps

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

from app.engines.vision.models.dlinknet import DLinkNet34


# ============================================================
# CONFIGURATION
# ============================================================

SPLIT_FILE = Path(
    "generated/deepglobe_split.json"
)

BASE_CHECKPOINT = Path(
    "models/dlinknet/log01_dink34.th"
)

OUTPUT_DIR = Path(
    "models/dlinknet/finetuned_deepglobe"
)

BEST_CHECKPOINT = (
    OUTPUT_DIR
    / "dlinknet34_deepglobe_best.pth"
)

LAST_CHECKPOINT = (
    OUTPUT_DIR
    / "dlinknet34_deepglobe_last.pth"
)

HISTORY_FILE = (
    OUTPUT_DIR
    / "training_history.json"
)

SEED = 42

# ------------------------------------------------------------
# Training
# ------------------------------------------------------------

EPOCHS = 10

BATCH_SIZE = 1

ACCUMULATION_STEPS = 4

LEARNING_RATE = 1e-5

WEIGHT_DECAY = 1e-4

# Validation is initially limited for practical CPU runtime.
# Final evaluation will use the frozen full validation/test sets.
VALIDATION_LIMIT = 100

# ------------------------------------------------------------
# Loss
# ------------------------------------------------------------

BCE_WEIGHT = 0.5

DICE_WEIGHT = 0.5

# ------------------------------------------------------------
# Threshold
# ------------------------------------------------------------

VALIDATION_THRESHOLD = 0.50


# ============================================================
# REPRODUCIBILITY
# ============================================================

def seed_everything(seed):

    random.seed(seed)

    np.random.seed(seed)

    torch.manual_seed(seed)

    if torch.cuda.is_available():

        torch.cuda.manual_seed_all(
            seed
        )


# ============================================================
# DATASET
# ============================================================

class DeepGlobeDataset(Dataset):

    def __init__(
        self,
        pairs,
        augment=False,
    ):

        self.pairs = pairs

        self.augment = augment

        self.mean = np.array(
            [
                0.485,
                0.456,
                0.406,
            ],
            dtype=np.float32,
        )

        self.std = np.array(
            [
                0.229,
                0.224,
                0.225,
            ],
            dtype=np.float32,
        )

    def __len__(self):

        return len(self.pairs)

    def __getitem__(
        self,
        index,
    ):

        item = self.pairs[index]

        image_path = Path(
            item["image"]
        )

        mask_path = Path(
            item["mask"]
        )

        image = Image.open(
            image_path
        ).convert("RGB")

        mask = Image.open(
            mask_path
        ).convert("L")

        # ----------------------------------------------------
        # Deterministic spatial augmentation
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

            rotation = random.choice(
                [
                    0,
                    90,
                    180,
                    270,
                ]
            )

            if rotation != 0:

                image = image.rotate(
                    rotation,
                    resample=Image.Resampling.BILINEAR,
                )

                mask = mask.rotate(
                    rotation,
                    resample=Image.Resampling.NEAREST,
                )

        # ----------------------------------------------------
        # RGB tensor
        # ----------------------------------------------------

        image_array = (
            np.asarray(
                image,
                dtype=np.float32,
            )
            / 255.0
        )

        image_array = (
            image_array
            - self.mean
        ) / self.std

        image_tensor = (
            torch.from_numpy(
                image_array
            )
            .permute(2, 0, 1)
            .contiguous()
            .float()
        )

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

        mask_tensor = (
            torch.from_numpy(
                mask_array
            )
            .unsqueeze(0)
            .contiguous()
            .float()
        )

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
    smooth=1.0,
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
        probabilities
        * targets
    ).sum(
        dim=1
    )

    denominator = (
        probabilities.sum(dim=1)
        + targets.sum(dim=1)
    )

    dice = (
        (
            2.0 * intersection
            + smooth
        )
        /
        (
            denominator
            + smooth
        )
    )

    return (
        1.0
        - dice.mean()
    )


# ============================================================
# COMBINED LOSS
# ============================================================

def segmentation_loss(
    logits,
    targets,
):

    bce = F.binary_cross_entropy_with_logits(
        logits,
        targets,
    )

    dice = dice_loss(
        logits,
        targets,
    )

    return (
        BCE_WEIGHT * bce
        +
        DICE_WEIGHT * dice
    )


# ============================================================
# METRICS
# ============================================================

def calculate_metrics(
    logits,
    targets,
    threshold=0.5,
):

    probabilities = torch.sigmoid(
        logits
    )

    predictions = (
        probabilities
        >= threshold
    )

    targets = (
        targets >= 0.5
    )

    tp = (
        predictions
        & targets
    ).sum().item()

    fp = (
        predictions
        & ~targets
    ).sum().item()

    fn = (
        ~predictions
        & targets
    ).sum().item()

    union = (
        tp + fp + fn
    )

    dice_denominator = (
        2 * tp
        + fp
        + fn
    )

    iou = (
        tp / union
        if union > 0
        else 1.0
    )

    dice = (
        2 * tp
        / dice_denominator
        if dice_denominator > 0
        else 1.0
    )

    precision = (
        tp / (tp + fp)
        if tp + fp > 0
        else 0.0
    )

    recall = (
        tp / (tp + fn)
        if tp + fn > 0
        else 0.0
    )

    return (
        iou,
        dice,
        precision,
        recall,
    )


# ============================================================
# LOAD CHECKPOINT
# ============================================================

def load_base_checkpoint(
    model,
):

    print()
    print(
        "Loading existing D-LinkNet34 checkpoint..."
    )

    checkpoint = torch.load(
        BASE_CHECKPOINT,
        map_location="cpu",
    )

    if isinstance(
        checkpoint,
        dict
    ) and "state_dict" in checkpoint:

        state_dict = checkpoint[
            "state_dict"
        ]

    else:

        state_dict = checkpoint

    cleaned_state_dict = {}

    for key, value in state_dict.items():

        clean_key = key

        if clean_key.startswith(
            "module."
        ):

            clean_key = (
                clean_key[7:]
            )

        cleaned_state_dict[
            clean_key
        ] = value

    model.load_state_dict(
        cleaned_state_dict,
        strict=True,
    )

    print(
        "Base checkpoint loaded."
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

    total_loss = 0.0

    total_iou = 0.0

    total_dice = 0.0

    total_precision = 0.0

    total_recall = 0.0

    count = 0

    with torch.no_grad():

        for (
            images,
            masks,
        ) in loader:

            images = images.to(
                device,
                non_blocking=True,
            )

            masks = masks.to(
                device,
                non_blocking=True,
            )

            logits = model(
                images
            )

            loss = segmentation_loss(
                logits,
                masks,
            )

            (
                iou,
                dice,
                precision,
                recall,
            ) = calculate_metrics(
                logits,
                masks,
                VALIDATION_THRESHOLD,
            )

            total_loss += (
                loss.item()
            )

            total_iou += iou

            total_dice += dice

            total_precision += (
                precision
            )

            total_recall += recall

            count += 1

    if count == 0:

        return (
            0,
            0,
            0,
            0,
            0,
        )

    return (
        total_loss / count,
        total_iou / count,
        total_dice / count,
        total_precision / count,
        total_recall / count,
    )


# ============================================================
# SAVE CHECKPOINT
# ============================================================

def save_checkpoint(
    path,
    model,
    optimizer,
    scheduler,
    epoch,
    best_iou,
    history,
):

    torch.save(
        {
            "epoch": epoch,
            "model_state_dict":
                model.state_dict(),
            "optimizer_state_dict":
                optimizer.state_dict(),
            "scheduler_state_dict":
                scheduler.state_dict()
                if scheduler is not None
                else None,
            "best_iou": best_iou,
            "history": history,
        },
        path,
    )


# ============================================================
# MAIN
# ============================================================

def main():

    seed_everything(
        SEED
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("=" * 70)
    print(
        "ATLAS — D-LINKNET34 DEEPGLOBE FINE-TUNING"
    )
    print("=" * 70)

    # ========================================================
    # DEVICE
    # ========================================================

    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    print(
        f"Device: {device}"
    )

    if device.type == "cuda":

        print(
            f"GPU: "
            f"{torch.cuda.get_device_name(0)}"
        )

    else:

        print(
            "WARNING: CPU training."
        )

        print(
            "This will be slow."
        )

    # ========================================================
    # LOAD SPLIT
    # ========================================================

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
    ]

    validation_pairs = split[
        "validation"
    ]

    # --------------------------------------------------------
    # Practical training validation subset
    # --------------------------------------------------------

    if (
        VALIDATION_LIMIT is not None
        and len(validation_pairs)
        > VALIDATION_LIMIT
    ):

        rng = np.random.default_rng(
            SEED
        )

        indices = rng.choice(
            len(validation_pairs),
            size=VALIDATION_LIMIT,
            replace=False,
        )

        indices.sort()

        validation_pairs = [
            validation_pairs[i]
            for i in indices
        ]

    print()
    print(
        "DATASET"
    )

    print(
        f"Training images   : "
        f"{len(train_pairs)}"
    )

    print(
        f"Validation images : "
        f"{len(validation_pairs)}"
    )

    # ========================================================
    # DATASETS
    # ========================================================

    train_dataset = (
        DeepGlobeDataset(
            train_pairs,
            augment=True,
        )
    )

    validation_dataset = (
        DeepGlobeDataset(
            validation_pairs,
            augment=False,
        )
    )

    # --------------------------------------------------------
    # DataLoaders
    # --------------------------------------------------------

    workers = (
        2
        if device.type == "cuda"
        else 0
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=workers,
        pin_memory=(
            device.type == "cuda"
        ),
    )

    validation_loader = DataLoader(
        validation_dataset,
        batch_size=1,
        shuffle=False,
        num_workers=workers,
        pin_memory=(
            device.type == "cuda"
        ),
    )

    # ========================================================
    # MODEL
    # ========================================================

    print()
    print(
        "Building D-LinkNet34..."
    )

    model = DLinkNet34(
        num_classes=1,
        pretrained_encoder=False,
    )

    load_base_checkpoint(
        model
    )

    model.to(
        device
    )

    # ========================================================
    # OPTIMIZER
    # ========================================================

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY,
    )

    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer,
        T_max=EPOCHS,
        eta_min=1e-7,
    )

    # ========================================================
    # AMP
    # ========================================================

    use_amp = (
        device.type == "cuda"
    )

    scaler = torch.cuda.amp.GradScaler(
        enabled=use_amp
    )

    # ========================================================
    # TRAIN
    # ========================================================

    best_iou = -1.0

    history = []

    print()
    print(
        "TRAINING START"
    )

    print(
        f"Epochs: {EPOCHS}"
    )

    print(
        f"Learning rate: "
        f"{LEARNING_RATE}"
    )

    print(
        f"Batch size: "
        f"{BATCH_SIZE}"
    )

    print(
        f"Gradient accumulation: "
        f"{ACCUMULATION_STEPS}"
    )

    print()

    for epoch in range(
        1,
        EPOCHS + 1,
    ):

        epoch_start = (
            time.perf_counter()
        )

        model.train()

        running_loss = 0.0

        optimizer.zero_grad(
            set_to_none=True
        )

        for step, (
            images,
            masks,
        ) in enumerate(
            train_loader,
            start=1,
        ):

            images = images.to(
                device,
                non_blocking=True,
            )

            masks = masks.to(
                device,
                non_blocking=True,
            )

            with torch.autocast(
                device_type="cuda"
                if device.type == "cuda"
                else "cpu",
                enabled=use_amp,
            ):

                logits = model(
                    images
                )

                loss = segmentation_loss(
                    logits,
                    masks,
                )

                loss = (
                    loss
                    / ACCUMULATION_STEPS
                )

            scaler.scale(
                loss
            ).backward()

            if (
                step
                % ACCUMULATION_STEPS
                == 0
                or step
                == len(train_loader)
            ):

                scaler.unscale_(
                    optimizer
                )

                torch.nn.utils.clip_grad_norm_(
                    model.parameters(),
                    max_norm=1.0,
                )

                scaler.step(
                    optimizer
                )

                scaler.update()

                optimizer.zero_grad(
                    set_to_none=True
                )

            running_loss += (
                loss.item()
                * ACCUMULATION_STEPS
            )

            if (
                step % 100 == 0
            ):

                print(
                    f"Epoch "
                    f"{epoch}/{EPOCHS} | "
                    f"Step "
                    f"{step}/{len(train_loader)} | "
                    f"Loss "
                    f"{running_loss / step:.5f}"
                )

        scheduler.step()

        train_loss = (
            running_loss
            / len(train_loader)
        )

        # ----------------------------------------------------
        # Validation
        # ----------------------------------------------------

        (
            val_loss,
            val_iou,
            val_dice,
            val_precision,
            val_recall,
        ) = validate(
            model,
            validation_loader,
            device,
        )

        epoch_time = (
            time.perf_counter()
            - epoch_start
        )

        current_lr = (
            optimizer.param_groups[0][
                "lr"
            ]
        )

        record = {

            "epoch": epoch,

            "train_loss":
                float(train_loss),

            "validation_loss":
                float(val_loss),

            "validation_iou":
                float(val_iou),

            "validation_dice":
                float(val_dice),

            "validation_precision":
                float(
                    val_precision
                ),

            "validation_recall":
                float(
                    val_recall
                ),

            "learning_rate":
                float(current_lr),

            "epoch_seconds":
                float(epoch_time),
        }

        history.append(
            record
        )

        print()
        print("=" * 70)
        print(
            f"EPOCH {epoch}/{EPOCHS}"
        )
        print("=" * 70)

        print(
            f"Train loss : "
            f"{train_loss:.5f}"
        )

        print(
            f"Val loss   : "
            f"{val_loss:.5f}"
        )

        print(
            f"Val IoU    : "
            f"{val_iou:.4f}"
        )

        print(
            f"Val Dice   : "
            f"{val_dice:.4f}"
        )

        print(
            f"Precision  : "
            f"{val_precision:.4f}"
        )

        print(
            f"Recall     : "
            f"{val_recall:.4f}"
        )

        print(
            f"LR         : "
            f"{current_lr:.8f}"
        )

        print(
            f"Time       : "
            f"{epoch_time:.1f}s"
        )

        # ----------------------------------------------------
        # Save last
        # ----------------------------------------------------

        save_checkpoint(
            LAST_CHECKPOINT,
            model,
            optimizer,
            scheduler,
            epoch,
            best_iou,
            history,
        )

        # ----------------------------------------------------
        # Save best
        # ----------------------------------------------------

        if val_iou > best_iou:

            best_iou = val_iou

            save_checkpoint(
                BEST_CHECKPOINT,
                model,
                optimizer,
                scheduler,
                epoch,
                best_iou,
                history,
            )

            print()
            print(
                "NEW BEST CHECKPOINT"
            )

            print(
                f"Best IoU: "
                f"{best_iou:.4f}"
            )

        # ----------------------------------------------------
        # History
        # ----------------------------------------------------

        with open(
            HISTORY_FILE,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                history,
                file,
                indent=4,
            )

        print()

    # ========================================================
    # COMPLETE
    # ========================================================

    print("=" * 70)
    print(
        "D-LINKNET FINE-TUNING COMPLETE"
    )
    print("=" * 70)

    print(
        f"Best validation IoU: "
        f"{best_iou:.4f}"
    )

    print(
        f"Best checkpoint: "
        f"{BEST_CHECKPOINT}"
    )

    print(
        f"Last checkpoint: "
        f"{LAST_CHECKPOINT}"
    )

    print(
        f"History: "
        f"{HISTORY_FILE}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()