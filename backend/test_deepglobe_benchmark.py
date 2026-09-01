from pathlib import Path
import time

import numpy as np
from PIL import Image

from app.engines.vision.registry import ModelRegistry


# ============================================================
# CONFIGURATION
# ============================================================

DATASET_ROOT = Path(
    r"D:\Projects\atlas\datasets\DeepGlobe"
)

TRAIN_DIR = DATASET_ROOT / "train"

MODELS = [
    "openearthmap",
    "dlinknet34",
    "roadgie",
]

# Start with 20 images to verify everything works.
# After successful testing, change to None.
MAX_IMAGES = 20

# Fraction of labeled train data used for validation.
VALIDATION_FRACTION = 0.20

# Deterministic split.
RANDOM_SEED = 42

THRESHOLD = 0.50


# ============================================================
# DATASET
# ============================================================

def find_labeled_pairs():

    image_paths = sorted(
        TRAIN_DIR.glob("*_sat.jpg")
    )

    pairs = []

    for image_path in image_paths:

        image_id = image_path.stem.replace(
            "_sat",
            "",
        )

        mask_path = (
            TRAIN_DIR
            / f"{image_id}_mask.png"
        )

        if mask_path.exists():

            pairs.append(
                (
                    image_path,
                    mask_path,
                )
            )

    return pairs


def create_validation_split(pairs):

    if not pairs:
        raise RuntimeError(
            f"No labeled image/mask pairs found in:\n"
            f"{TRAIN_DIR}"
        )

    rng = np.random.default_rng(
        RANDOM_SEED
    )

    indices = np.arange(
        len(pairs)
    )

    rng.shuffle(indices)

    validation_count = max(
        1,
        int(
            len(pairs)
            * VALIDATION_FRACTION
        ),
    )

    validation_indices = indices[
        :validation_count
    ]

    validation_pairs = [
        pairs[i]
        for i in validation_indices
    ]

    return validation_pairs


# ============================================================
# GROUND TRUTH
# ============================================================

def load_ground_truth(mask_path):

    mask = np.array(
        Image.open(
            mask_path
        ).convert("L")
    )

    return mask > 127


# ============================================================
# PROBABILITY MAP
# ============================================================

def normalize_probability(
    probability,
    image_size,
    model_name,
):
    probability = np.asarray(
        probability
    )

    # --------------------------------------------------------
    # Remove batch dimension when present
    # --------------------------------------------------------

    if probability.ndim == 4:
        # [B, C, H, W]
        probability = probability[0]

    # --------------------------------------------------------
    # OpenEarthMap semantic output
    # --------------------------------------------------------
    #
    # [C, H, W]
    #
    # Road class = 4
    # --------------------------------------------------------

    if model_name == "openearthmap":

        if probability.ndim != 3:
            raise RuntimeError(
                "Expected OpenEarthMap output "
                f"[C,H,W], got {probability.shape}"
            )

        road_class_id = 4

        if probability.shape[0] <= road_class_id:
            raise RuntimeError(
                "OpenEarthMap output does not "
                f"contain road class {road_class_id}. "
                f"Shape: {probability.shape}"
            )

        probability = probability[
            road_class_id
        ]

    # --------------------------------------------------------
    # Binary road models
    # --------------------------------------------------------

    else:

        probability = np.squeeze(
            probability
        )

        if probability.ndim != 2:
            raise RuntimeError(
                f"{model_name} should produce "
                f"a 2D probability map, got "
                f"{probability.shape}"
            )

    # --------------------------------------------------------
    # Resize to original image
    # --------------------------------------------------------

    target_width, target_height = (
        image_size
    )

    if probability.shape != (
        target_height,
        target_width,
    ):

        probability_image = (
            Image.fromarray(
                probability.astype(
                    np.float32
                ),
                mode="F",
            )
        )

        probability_image = (
            probability_image.resize(
                (
                    target_width,
                    target_height,
                ),
                Image.Resampling.BILINEAR,
            )
        )

        probability = np.asarray(
            probability_image,
            dtype=np.float32,
        )

    return probability.astype(
        np.float32
    )
# ============================================================
# METRICS
# ============================================================

def calculate_metrics(
    prediction,
    ground_truth,
):

    prediction = prediction.astype(
        bool
    )

    ground_truth = ground_truth.astype(
        bool
    )

    tp = np.logical_and(
        prediction,
        ground_truth,
    ).sum()

    fp = np.logical_and(
        prediction,
        ~ground_truth,
    ).sum()

    fn = np.logical_and(
        ~prediction,
        ground_truth,
    ).sum()

    intersection = tp

    union = (
        prediction.sum()
        + ground_truth.sum()
        - intersection
    )

    iou = (
        intersection / union
        if union > 0
        else 1.0
    )

    dice_denominator = (
        prediction.sum()
        + ground_truth.sum()
    )

    dice = (
        (2.0 * intersection)
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

    return {
        "iou": float(iou),
        "dice": float(dice),
        "precision": float(precision),
        "recall": float(recall),
    }


# ============================================================
# MODEL EVALUATION
# ============================================================

def evaluate_model(
    model_name,
    validation_pairs,
):

    print()
    print("=" * 70)
    print(
        f"MODEL: {model_name}"
    )
    print("=" * 70)

    predictor = ModelRegistry.get(
        model_name
    )

    totals = {
        "iou": [],
        "dice": [],
        "precision": [],
        "recall": [],
        "inference_ms": [],
    }

    for index, (
        image_path,
        mask_path,
    ) in enumerate(
        validation_pairs,
        start=1,
    ):

        print(
            f"[{index}/{len(validation_pairs)}] "
            f"{image_path.name}"
        )

        image = Image.open(
            image_path
        ).convert("RGB")

        ground_truth = (
            load_ground_truth(
                mask_path
            )
        )

        start = time.perf_counter()

        result = predictor.predict(
            image
        )

        elapsed_ms = (
            time.perf_counter()
            - start
        ) * 1000.0

        probability = getattr(
            result,
            "logits",
            None,
        )

        if probability is None:

            raise RuntimeError(
                f"{model_name} did not return "
                "a probability map through "
                "SegmentationResult.logits."
            )

        probability = (
            normalize_probability(
                probability,
                image.size,
                model_name
            )
        )

        prediction = (
            probability >= THRESHOLD
        )

        metrics = calculate_metrics(
            prediction,
            ground_truth,
        )

        totals["iou"].append(
            metrics["iou"]
        )

        totals["dice"].append(
            metrics["dice"]
        )

        totals["precision"].append(
            metrics["precision"]
        )

        totals["recall"].append(
            metrics["recall"]
        )

        totals[
            "inference_ms"
        ].append(
            elapsed_ms
        )

    print()
    print("-" * 70)

    print(
        f"IoU       : "
        f"{np.mean(totals['iou']):.4f}"
    )

    print(
        f"Dice      : "
        f"{np.mean(totals['dice']):.4f}"
    )

    print(
        f"Precision : "
        f"{np.mean(totals['precision']):.4f}"
    )

    print(
        f"Recall    : "
        f"{np.mean(totals['recall']):.4f}"
    )

    print(
        f"Inference : "
        f"{np.mean(totals['inference_ms']):.2f} ms"
    )

    return totals


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print(
        "ATLAS — DEEPGLOBE ROAD ACCURACY BENCHMARK"
    )
    print("=" * 70)

    print(
        f"Dataset: {TRAIN_DIR}"
    )

    # --------------------------------------------------------
    # Find labeled data
    # --------------------------------------------------------

    pairs = find_labeled_pairs()

    print(
        f"Labeled image/mask pairs: "
        f"{len(pairs)}"
    )

    if not pairs:

        raise RuntimeError(
            "No labeled DeepGlobe pairs found."
        )

    # --------------------------------------------------------
    # Create deterministic validation subset
    # --------------------------------------------------------

    validation_pairs = (
        create_validation_split(
            pairs
        )
    )

    if (
        MAX_IMAGES is not None
        and len(validation_pairs)
        > MAX_IMAGES
    ):

        validation_pairs = (
            validation_pairs[
                :MAX_IMAGES
            ]
        )

    print(
        f"Benchmark validation images: "
        f"{len(validation_pairs)}"
    )

    print(
        f"Random seed: {RANDOM_SEED}"
    )

    print(
        f"Threshold: {THRESHOLD}"
    )

    # --------------------------------------------------------
    # Evaluate models
    # --------------------------------------------------------

    results = {}

    for model_name in MODELS:

        results[model_name] = (
            evaluate_model(
                model_name,
                validation_pairs,
            )
        )

    # --------------------------------------------------------
    # Final comparison
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print(
        "FINAL BASELINE COMPARISON"
    )
    print("=" * 70)

    print(
        f"{'MODEL':<18}"
        f"{'IoU':>10}"
        f"{'Dice':>10}"
        f"{'Precision':>12}"
        f"{'Recall':>10}"
    )

    print("-" * 60)

    for model_name, metrics in (
        results.items()
    ):

        print(
            f"{model_name:<18}"
            f"{np.mean(metrics['iou']):>10.4f}"
            f"{np.mean(metrics['dice']):>10.4f}"
            f"{np.mean(metrics['precision']):>12.4f}"
            f"{np.mean(metrics['recall']):>10.4f}"
        )

    print("=" * 70)
    print(
        "BENCHMARK COMPLETE"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()