from pathlib import Path
import json
import random
import time

import numpy as np
from PIL import Image, ImageOps

import torch
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

from app.engines.vision.models.dlinknet import DLinkNet34


# ============================================================
# CONFIG
# ============================================================

SPLIT_FILE = Path(
    "generated/deepglobe_split.json"
)

BASE_CHECKPOINT = Path(
    "models/dlinknet/log01_dink34.th"
)

OUTPUT_DIR = Path(
    "models/dlinknet/finetuned_500"
)

BEST_CHECKPOINT = (
    OUTPUT_DIR /
    "dlinknet34_deepglobe_500_best.pth"
)

LAST_CHECKPOINT = (
    OUTPUT_DIR /
    "dlinknet34_deepglobe_500_last.pth"
)

HISTORY_FILE = (
    OUTPUT_DIR /
    "training_history.json"
)

SEED = 42

TRAIN_COUNT = 500
VALIDATION_COUNT = 100

IMAGE_SIZE = 512

EPOCHS = 3

BATCH_SIZE = 1

LEARNING_RATE = 1e-5

WEIGHT_DECAY = 1e-4

PRINT_EVERY = 25


# ============================================================
# SEED
# ============================================================

def seed_everything(seed):

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


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
            [0.485, 0.456, 0.406],
            dtype=np.float32,
        )

        self.std = np.array(
            [0.229, 0.224, 0.225],
            dtype=np.float32,
        )

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, index):

        item = self.pairs[index]

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
                [0, 90, 180, 270]
            )

            if rotation:

                image = image.rotate(
                    rotation,
                    resample=Image.Resampling.BILINEAR,
                )

                mask = mask.rotate(
                    rotation,
                    resample=Image.Resampling.NEAREST,
                )

        image_array = (
            np.asarray(
                image,
                dtype=np.float32,
            ) / 255.0
        )

        image_array = (
            image_array - self.mean
        ) / self.std

        image_tensor = torch.from_numpy(
            image_array
        ).permute(
            2, 0, 1
        ).float()

        mask_array = (
            np.asarray(
                mask,
                dtype=np.uint8,
            ) > 127
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
# LOSS
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
    ).sum(dim=1)

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


def loss_function(
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
        0.5 * bce
        +
        0.5 * dice
    )


# ============================================================
# METRICS
# ============================================================

def calculate_metrics(
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

    union = tp + fp + fn

    dice_denominator = (
        2 * tp + fp + fn
    )

    iou = (
        tp / union
        if union > 0
        else 1.0
    )

    dice = (
        2 * tp / dice_denominator
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
# CHECKPOINT
# ============================================================

def load_checkpoint(model):

    print()
    print(
        "Loading existing D-LinkNet34..."
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

        if key.startswith("module."):
            key = key[7:]

        cleaned[key] = value

    model.load_state_dict(
        cleaned,
        strict=True,
    )

    print(
        "Base checkpoint loaded."
    )


def save_checkpoint(
    path,
    model,
    optimizer,
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
            "best_iou":
                best_iou,
            "history":
                history,
        },
        path,
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

    with torch.no_grad():

        for images, masks in loader:

            images = images.to(device)
            masks = masks.to(device)

            logits = model(images)

            loss = loss_function(
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
            )

            total_loss += loss.item()
            total_iou += iou
            total_dice += dice
            total_precision += precision
            total_recall += recall

    count = len(loader)

    return (
        total_loss / count,
        total_iou / count,
        total_dice / count,
        total_precision / count,
        total_recall / count,
    )


# ============================================================
# MAIN
# ============================================================

def main():

    seed_everything(SEED)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("=" * 70)
    print(
        "ATLAS — D-LINKNET34 CONTROLLED FINE-TUNING"
    )
    print("=" * 70)

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
            "CPU mode."
        )

    # --------------------------------------------------------
    # Split
    # --------------------------------------------------------

    with open(
        SPLIT_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        split = json.load(file)

    rng_train = np.random.default_rng(
        SEED
    )

    rng_val = np.random.default_rng(
        SEED + 1
    )

    train_indices = rng_train.choice(
        len(split["train"]),
        size=min(
            TRAIN_COUNT,
            len(split["train"]),
        ),
        replace=False,
    )

    val_indices = rng_val.choice(
        len(split["validation"]),
        size=min(
            VALIDATION_COUNT,
            len(split["validation"]),
        ),
        replace=False,
    )

    train_indices.sort()
    val_indices.sort()

    train_pairs = [
        split["train"][i]
        for i in train_indices
    ]

    validation_pairs = [
        split["validation"][i]
        for i in val_indices
    ]

    print()
    print(
        "DATASET"
    )

    print(
        f"Training   : "
        f"{len(train_pairs)}"
    )

    print(
        f"Validation : "
        f"{len(validation_pairs)}"
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

    train_dataset = DeepGlobeDataset(
        train_pairs,
        augment=True,
    )

    validation_dataset = DeepGlobeDataset(
        validation_pairs,
        augment=False,
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

    load_checkpoint(model)

    model.to(device)

    # --------------------------------------------------------
    # Baseline
    # --------------------------------------------------------

    print()
    print(
        "VALIDATION BEFORE FINE-TUNING"
    )

    (
        baseline_loss,
        baseline_iou,
        baseline_dice,
        baseline_precision,
        baseline_recall,
    ) = validate(
        model,
        validation_loader,
        device,
    )

    print(
        f"IoU       : {baseline_iou:.4f}"
    )

    print(
        f"Dice      : {baseline_dice:.4f}"
    )

    print(
        f"Precision : {baseline_precision:.4f}"
    )

    print(
        f"Recall    : {baseline_recall:.4f}"
    )

    # --------------------------------------------------------
    # Optimizer
    # --------------------------------------------------------

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY,
    )

    best_iou = baseline_iou

    history = []

    # --------------------------------------------------------
    # Training
    # --------------------------------------------------------

    print()
    print(
        "=" * 70
    )

    print(
        "TRAINING START"
    )

    print(
        "=" * 70
    )

    for epoch in range(
        1,
        EPOCHS + 1,
    ):

        epoch_start = time.perf_counter()

        model.train()

        running_loss = 0.0

        for step, (
            images,
            masks,
        ) in enumerate(
            train_loader,
            start=1,
        ):

            step_start = time.perf_counter()

            images = images.to(device)
            masks = masks.to(device)

            optimizer.zero_grad(
                set_to_none=True
            )

            logits = model(images)

            loss = loss_function(
                logits,
                masks,
            )

            loss.backward()

            optimizer.step()

            running_loss += loss.item()

            if (
                step % PRINT_EVERY == 0
                or step == 1
                or step == len(train_loader)
            ):

                elapsed = (
                    time.perf_counter()
                    - step_start
                )

                print(
                    f"[Epoch {epoch}/{EPOCHS}] "
                    f"[{step}/{len(train_loader)}] "
                    f"Loss={loss.item():.5f} "
                    f"Step={elapsed:.2f}s"
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

        train_loss = (
            running_loss
            / len(train_loader)
        )

        record = {
            "epoch": epoch,
            "train_loss": float(train_loss),
            "validation_loss": float(val_loss),
            "validation_iou": float(val_iou),
            "validation_dice": float(val_dice),
            "validation_precision":
                float(val_precision),
            "validation_recall":
                float(val_recall),
            "seconds":
                float(epoch_time),
        }

        history.append(record)

        print()
        print("=" * 70)
        print(
            f"EPOCH {epoch}/{EPOCHS}"
        )
        print("=" * 70)

        print(
            f"Train loss : {train_loss:.5f}"
        )

        print(
            f"Val IoU    : {val_iou:.4f}"
        )

        print(
            f"Val Dice   : {val_dice:.4f}"
        )

        print(
            f"Precision  : {val_precision:.4f}"
        )

        print(
            f"Recall     : {val_recall:.4f}"
        )

        print(
            f"Time       : {epoch_time:.1f}s"
        )

        # ----------------------------------------------------
        # Save last
        # ----------------------------------------------------

        save_checkpoint(
            LAST_CHECKPOINT,
            model,
            optimizer,
            epoch,
            best_iou,
            history,
        )

        # ----------------------------------------------------
        # Best
        # ----------------------------------------------------

        if val_iou > best_iou:

            best_iou = val_iou

            save_checkpoint(
                BEST_CHECKPOINT,
                model,
                optimizer,
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

    # --------------------------------------------------------
    # Final report
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print(
        "CONTROLLED FINE-TUNING COMPLETE"
    )
    print("=" * 70)

    print(
        f"Original validation IoU : "
        f"{baseline_iou:.4f}"
    )

    print(
        f"Best fine-tuned IoU     : "
        f"{best_iou:.4f}"
    )

    print(
        f"Improvement             : "
        f"{best_iou - baseline_iou:+.4f}"
    )

    print()
    print(
        f"Best checkpoint:"
    )

    print(
        BEST_CHECKPOINT
    )

    print("=" * 70)


if __name__ == "__main__":
    main()