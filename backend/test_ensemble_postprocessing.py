from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

from app.engines.vision.registry import ModelRegistry


# ============================================================
# CONFIG
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

MAX_IMAGES = 20

RANDOM_SEED = 42

# Current best ensemble from previous experiment.
BASE_WEIGHTS = np.array(
    [0.00, 0.65, 0.35],
    dtype=np.float32,
)

BASE_THRESHOLD = 0.30

BASELINE_IOU = 0.4998

BASELINE_DICE = 0.6440


# ============================================================
# DATASET
# ============================================================

def find_pairs():

    images = sorted(
        TRAIN_DIR.glob("*_sat.jpg")
    )

    pairs = []

    for image_path in images:

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


def validation_split(pairs):

    rng = np.random.default_rng(
        RANDOM_SEED
    )

    indices = np.arange(
        len(pairs)
    )

    rng.shuffle(indices)

    selected = indices[
        :MAX_IMAGES
    ]

    return [
        pairs[i]
        for i in selected
    ]


# ============================================================
# PROBABILITY EXTRACTION
# ============================================================

def extract_probability(
    result,
    model_name,
    image_size,
):

    probability = np.asarray(
        result.logits
    )

    if probability.ndim == 4:

        probability = probability[0]

    if model_name == "openearthmap":

        if probability.ndim != 3:

            raise RuntimeError(
                "Unexpected OpenEarthMap "
                f"shape: {probability.shape}"
            )

        # Road class = 4
        probability = probability[4]

    else:

        probability = np.squeeze(
            probability
        )

    if probability.ndim != 2:

        raise RuntimeError(
            f"{model_name} probability "
            f"shape: {probability.shape}"
        )

    width, height = image_size

    if probability.shape != (
        height,
        width,
    ):

        probability = np.asarray(
            Image.fromarray(
                probability.astype(
                    np.float32
                ),
                mode="F",
            ).resize(
                (
                    width,
                    height,
                ),
                Image.Resampling.BILINEAR,
            ),
            dtype=np.float32,
        )

    return probability.astype(
        np.float32
    )


# ============================================================
# COLLECT MODEL OUTPUTS
# ============================================================

def collect_predictions(
    pairs,
):

    predictors = {}

    for model_name in MODELS:

        print()
        print(
            f"Loading {model_name}..."
        )

        predictors[
            model_name
        ] = ModelRegistry.get(
            model_name
        )

    probabilities = []

    ground_truths = []

    for index, (
        image_path,
        mask_path,
    ) in enumerate(
        pairs,
        start=1,
    ):

        print(
            f"[{index}/{len(pairs)}] "
            f"{image_path.name}"
        )

        image = Image.open(
            image_path
        ).convert("RGB")

        ground_truth = (
            np.asarray(
                Image.open(
                    mask_path
                ).convert("L")
            )
            > 127
        )

        model_maps = []

        for model_name in MODELS:

            result = predictors[
                model_name
            ].predict(
                image
            )

            probability = (
                extract_probability(
                    result,
                    model_name,
                    image.size,
                )
            )

            model_maps.append(
                probability
            )

        probabilities.append(
            np.stack(
                model_maps,
                axis=0,
            )
        )

        ground_truths.append(
            ground_truth
        )

    probabilities = np.stack(
        probabilities,
        axis=0,
    )

    ground_truths = np.stack(
        ground_truths,
        axis=0,
    )

    return (
        probabilities,
        ground_truths,
    )


# ============================================================
# POST-PROCESSING
# ============================================================

def remove_small_components(
    mask,
    min_size,
):

    if min_size <= 0:

        return mask

    labels, count = (
        ndimage.label(
            mask,
            structure=np.ones(
                (3, 3),
                dtype=np.uint8,
            ),
        )
    )

    if count == 0:

        return mask

    component_sizes = np.bincount(
        labels.ravel()
    )

    keep = (
        component_sizes
        >= min_size
    )

    keep[0] = False

    return keep[
        labels
    ]


def postprocess_mask(
    mask,
    closing_iterations,
    min_component_size,
    fill_holes,
):

    processed = mask.astype(
        bool
    )

    # --------------------------------------------------------
    # Morphological closing
    #
    # Useful for:
    # - tiny breaks
    # - narrow gaps
    # - disconnected road boundaries
    # --------------------------------------------------------

    if closing_iterations > 0:

        structure = np.ones(
            (3, 3),
            dtype=bool,
        )

        processed = ndimage.binary_closing(
            processed,
            structure=structure,
            iterations=closing_iterations,
        )

    # --------------------------------------------------------
    # Fill enclosed holes
    # --------------------------------------------------------

    if fill_holes:

        processed = (
            ndimage.binary_fill_holes(
                processed
            )
        )

    # --------------------------------------------------------
    # Remove tiny isolated regions
    # --------------------------------------------------------

    if min_component_size > 0:

        processed = (
            remove_small_components(
                processed,
                min_component_size,
            )
        )

    return processed


# ============================================================
# METRICS
# ============================================================

def evaluate_mask(
    prediction,
    ground_truth,
):

    intersection = np.logical_and(
        prediction,
        ground_truth,
    ).sum()

    union = np.logical_or(
        prediction,
        ground_truth,
    ).sum()

    predicted_pixels = (
        prediction.sum()
    )

    ground_truth_pixels = (
        ground_truth.sum()
    )

    iou = (
        intersection / union
        if union > 0
        else 1.0
    )

    dice_denominator = (
        predicted_pixels
        + ground_truth_pixels
    )

    dice = (
        2.0 * intersection
        / dice_denominator
        if dice_denominator > 0
        else 1.0
    )

    tp = intersection

    fp = (
        predicted_pixels
        - intersection
    )

    fn = (
        ground_truth_pixels
        - intersection
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
        float(iou),
        float(dice),
        float(precision),
        float(recall),
    )


# ============================================================
# EVALUATE CONFIGURATION
# ============================================================

def evaluate_configuration(
    fused_maps,
    ground_truths,
    threshold,
    closing_iterations,
    min_component_size,
    fill_holes,
):

    ious = []
    dices = []
    precisions = []
    recalls = []

    for image_index in range(
        len(fused_maps)
    ):

        raw_mask = (
            fused_maps[
                image_index
            ]
            >= threshold
        )

        processed = postprocess_mask(
            raw_mask,
            closing_iterations,
            min_component_size,
            fill_holes,
        )

        (
            iou,
            dice,
            precision,
            recall,
        ) = evaluate_mask(
            processed,
            ground_truths[
                image_index
            ],
        )

        ious.append(iou)
        dices.append(dice)
        precisions.append(precision)
        recalls.append(recall)

    return (
        float(np.mean(ious)),
        float(np.mean(dices)),
        float(np.mean(precisions)),
        float(np.mean(recalls)),
    )


# ============================================================
# SEARCH
# ============================================================

def search_postprocessing(
    fused_maps,
    ground_truths,
):

    print()
    print(
        "=" * 70
    )

    print(
        "SEARCHING POST-PROCESSING"
    )

    print(
        "=" * 70
    )

    # --------------------------------------------------------
    # Deliberately centered around current threshold.
    # --------------------------------------------------------

    thresholds = np.arange(
        0.20,
        0.451,
        0.025,
        dtype=np.float32,
    )

    closing_values = [
        0,
        1,
        2,
    ]

    component_sizes = [
        0,
        25,
        50,
        100,
        250,
    ]

    hole_values = [
        False,
        True,
    ]

    total = (
        len(thresholds)
        * len(closing_values)
        * len(component_sizes)
        * len(hole_values)
    )

    print(
        f"Thresholds : "
        f"{len(thresholds)}"
    )

    print(
        f"Closing    : "
        f"{closing_values}"
    )

    print(
        f"Components : "
        f"{component_sizes}"
    )

    print(
        f"Hole fill  : "
        f"{hole_values}"
    )

    print(
        f"Total configurations: "
        f"{total}"
    )

    # --------------------------------------------------------
    # Baseline first.
    # --------------------------------------------------------

    best = {
        "iou": BASELINE_IOU,
        "dice": BASELINE_DICE,
        "precision": None,
        "recall": None,
        "threshold": BASE_THRESHOLD,
        "closing": 0,
        "min_component": 0,
        "fill_holes": False,
    }

    best_config_found = False

    checked = 0

    for threshold in thresholds:

        # ----------------------------------------------------
        # Create raw threshold mask ONCE.
        # ----------------------------------------------------

        raw_masks = (
            fused_maps
            >= threshold
        )

        for closing in closing_values:

            for min_component in (
                component_sizes
            ):

                for fill_holes in (
                    hole_values
                ):

                    checked += 1

                    ious = []
                    dices = []
                    precisions = []
                    recalls = []

                    for image_index in range(
                        len(raw_masks)
                    ):

                        processed = (
                            postprocess_mask(
                                raw_masks[
                                    image_index
                                ],
                                closing,
                                min_component,
                                fill_holes,
                            )
                        )

                        (
                            iou,
                            dice,
                            precision,
                            recall,
                        ) = evaluate_mask(
                            processed,
                            ground_truths[
                                image_index
                            ],
                        )

                        ious.append(
                            iou
                        )

                        dices.append(
                            dice
                        )

                        precisions.append(
                            precision
                        )

                        recalls.append(
                            recall
                        )

                    mean_iou = float(
                        np.mean(
                            ious
                        )
                    )

                    mean_dice = float(
                        np.mean(
                            dices
                        )
                    )

                    mean_precision = float(
                        np.mean(
                            precisions
                        )
                    )

                    mean_recall = float(
                        np.mean(
                            recalls
                        )
                    )

                    if mean_iou > best[
                        "iou"
                    ]:

                        best = {
                            "iou":
                                mean_iou,

                            "dice":
                                mean_dice,

                            "precision":
                                mean_precision,

                            "recall":
                                mean_recall,

                            "threshold":
                                float(
                                    threshold
                                ),

                            "closing":
                                closing,

                            "min_component":
                                min_component,

                            "fill_holes":
                                fill_holes,
                        }

                        best_config_found = True

                        print()
                        print(
                            "NEW BEST"
                        )

                        print(
                            f"IoU       : "
                            f"{mean_iou:.4f}"
                        )

                        print(
                            f"Dice      : "
                            f"{mean_dice:.4f}"
                        )

                        print(
                            f"Threshold : "
                            f"{threshold:.3f}"
                        )

                        print(
                            f"Closing   : "
                            f"{closing}"
                        )

                        print(
                            f"Min comp  : "
                            f"{min_component}"
                        )

                        print(
                            f"Holes     : "
                            f"{fill_holes}"
                        )

                    if (
                        checked % 25 == 0
                        or checked == total
                    ):

                        print(
                            f"Progress: "
                            f"{checked}/{total} "
                            f"| Best IoU: "
                            f"{best['iou']:.4f}"
                        )

    return best


# ============================================================
# BUILD FUSED MAP
# ============================================================

def build_fused_map(
    probabilities,
):

    return (
        BASE_WEIGHTS[0]
        * probabilities[:, 0]
        +
        BASE_WEIGHTS[1]
        * probabilities[:, 1]
        +
        BASE_WEIGHTS[2]
        * probabilities[:, 2]
    )


# ============================================================
# SAVE BEST MASK
# ============================================================

def save_best_masks(
    fused_maps,
    ground_truths,
    pairs,
    config,
):

    output_dir = Path(
        "generated/ensemble_postprocessed"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    for index in range(
        len(fused_maps)
    ):

        raw_mask = (
            fused_maps[index]
            >= config["threshold"]
        )

        processed = postprocess_mask(
            raw_mask,
            config["closing"],
            config["min_component"],
            config["fill_holes"],
        )

        output = (
            processed.astype(
                np.uint8
            )
            * 255
        )

        image_id = (
            pairs[index][0]
            .stem
            .replace(
                "_sat",
                "",
            )
        )

        output_path = (
            output_dir
            / f"{image_id}_ensemble.png"
        )

        Image.fromarray(
            output
        ).save(
            output_path
        )

    print()
    print(
        f"Saved masks to: "
        f"{output_dir}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)

    print(
        "ATLAS — ENSEMBLE POST-PROCESSING OPTIMIZATION"
    )

    print("=" * 70)

    pairs = find_pairs()

    if not pairs:

        raise RuntimeError(
            "No labeled DeepGlobe pairs found."
        )

    pairs = validation_split(
        pairs
    )

    print(
        f"Validation images: "
        f"{len(pairs)}"
    )

    # --------------------------------------------------------
    # Model inference ONCE.
    # --------------------------------------------------------

    (
        probabilities,
        ground_truths,
    ) = collect_predictions(
        pairs
    )

    print()
    print(
        f"Probability tensor: "
        f"{probabilities.shape}"
    )

    print(
        f"Ground truth tensor: "
        f"{ground_truths.shape}"
    )

    # --------------------------------------------------------
    # Build current best ensemble.
    # --------------------------------------------------------

    fused_maps = build_fused_map(
        probabilities
    )

    print()
    print(
        "BASE ENSEMBLE"
    )

    print(
        f"OpenEarthMap : "
        f"{BASE_WEIGHTS[0]:.2f}"
    )

    print(
        f"D-LinkNet34  : "
        f"{BASE_WEIGHTS[1]:.2f}"
    )

    print(
        f"RoadGIE      : "
        f"{BASE_WEIGHTS[2]:.2f}"
    )

    print(
        f"Threshold    : "
        f"{BASE_THRESHOLD:.3f}"
    )

    print(
        f"Known IoU    : "
        f"{BASELINE_IOU:.4f}"
    )

    print(
        f"Known Dice   : "
        f"{BASELINE_DICE:.4f}"
    )

    # --------------------------------------------------------
    # Search.
    # --------------------------------------------------------

    result = search_postprocessing(
        fused_maps,
        ground_truths,
    )

    # --------------------------------------------------------
    # Final result.
    # --------------------------------------------------------

    print()
    print("=" * 70)

    print(
        "BEST POST-PROCESSED ENSEMBLE"
    )

    print("=" * 70)

    print(
        f"OpenEarthMap : "
        f"{BASE_WEIGHTS[0]:.2f}"
    )

    print(
        f"D-LinkNet34  : "
        f"{BASE_WEIGHTS[1]:.2f}"
    )

    print(
        f"RoadGIE      : "
        f"{BASE_WEIGHTS[2]:.2f}"
    )

    print(
        f"Threshold    : "
        f"{result['threshold']:.3f}"
    )

    print(
        f"Closing      : "
        f"{result['closing']}"
    )

    print(
        f"Min component: "
        f"{result['min_component']}"
    )

    print(
        f"Fill holes   : "
        f"{result['fill_holes']}"
    )

    print()

    print(
        f"IoU          : "
        f"{result['iou']:.4f}"
    )

    print(
        f"Dice         : "
        f"{result['dice']:.4f}"
    )

    print(
        f"Precision    : "
        f"{result['precision']:.4f}"
    )

    print(
        f"Recall       : "
        f"{result['recall']:.4f}"
    )

    print()

    improvement = (
        result["iou"]
        - BASELINE_IOU
    )

    print(
        f"Baseline IoU : "
        f"{BASELINE_IOU:.4f}"
    )

    print(
        f"Improvement  : "
        f"{improvement:+.4f}"
    )

    if improvement > 0:

        print()
        print(
            "RESULT: POST-PROCESSING "
            "IMPROVES THE ENSEMBLE."
        )

        save_best_masks(
            fused_maps,
            ground_truths,
            pairs,
            result,
        )

    else:

        print()
        print(
            "RESULT: POST-PROCESSING DOES "
            "NOT BEAT THE CURRENT ENSEMBLE."
        )

        print(
            "Keep the original 0.4998 configuration."
        )

    print("=" * 70)


if __name__ == "__main__":
    main()