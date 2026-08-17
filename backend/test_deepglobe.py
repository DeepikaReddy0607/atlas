import base64
import io
import json
import zlib
from pathlib import Path

import numpy as np
from PIL import Image

from app.engines.vision.models.openearthmap import (
    OpenEarthMapPredictor,
)


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

IMAGE_PATH = Path(
    "imagery/train/img/10255_sat.jpg"
)

ANNOTATION_PATH = Path(
    "imagery/train/ann/10255_sat.jpg.json"
)

OUTPUT_DIR = Path(
    "generated/deepglobe"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ---------------------------------------------------------
# Decode DeepGlobe bitmap annotation
# ---------------------------------------------------------

def decode_bitmap(
    bitmap_data: str,
) -> np.ndarray:

    compressed = base64.b64decode(
        bitmap_data
    )

    decompressed = zlib.decompress(
        compressed
    )

    image = Image.open(
        io.BytesIO(decompressed)
    ).convert("L")

    mask = np.array(image)

    return mask > 0


# ---------------------------------------------------------
# Build full-size ground-truth road mask
# ---------------------------------------------------------

def load_ground_truth(
    annotation_path: Path,
    width: int,
    height: int,
) -> np.ndarray:

    with open(
        annotation_path,
        "r",
        encoding="utf-8",
    ) as f:
        annotation = json.load(f)

    ground_truth = np.zeros(
        (height, width),
        dtype=bool,
    )

    road_objects = [
        obj
        for obj in annotation["objects"]
        if obj.get("classTitle") == "road"
        and obj.get("geometryType") == "bitmap"
    ]

    print(
        f"Road objects found: "
        f"{len(road_objects)}"
    )

    for obj in road_objects:

        bitmap = obj["bitmap"]

        bitmap_mask = decode_bitmap(
            bitmap["data"]
        )

        origin = bitmap.get(
            "origin",
            [0, 0],
        )

        x = int(origin[0])
        y = int(origin[1])

        h, w = bitmap_mask.shape

        # Keep coordinates inside image
        x2 = min(
            x + w,
            width,
        )

        y2 = min(
            y + h,
            height,
        )

        crop_w = x2 - x
        crop_h = y2 - y

        if (
            crop_w <= 0
            or crop_h <= 0
        ):
            continue

        ground_truth[
            y:y2,
            x:x2,
        ] |= bitmap_mask[
            :crop_h,
            :crop_w,
        ]

    return ground_truth


# ---------------------------------------------------------
# IoU
# ---------------------------------------------------------

def calculate_iou(
    prediction: np.ndarray,
    ground_truth: np.ndarray,
) -> float:

    intersection = np.logical_and(
        prediction,
        ground_truth,
    ).sum()

    union = np.logical_or(
        prediction,
        ground_truth,
    ).sum()

    if union == 0:
        return 0.0

    return (
        intersection
        / union
    )


# ---------------------------------------------------------
# Precision
# ---------------------------------------------------------

def calculate_precision(
    prediction: np.ndarray,
    ground_truth: np.ndarray,
) -> float:

    true_positive = np.logical_and(
        prediction,
        ground_truth,
    ).sum()

    false_positive = np.logical_and(
        prediction,
        ~ground_truth,
    ).sum()

    denominator = (
        true_positive
        + false_positive
    )

    if denominator == 0:
        return 0.0

    return (
        true_positive
        / denominator
    )


# ---------------------------------------------------------
# Recall
# ---------------------------------------------------------

def calculate_recall(
    prediction: np.ndarray,
    ground_truth: np.ndarray,
) -> float:

    true_positive = np.logical_and(
        prediction,
        ground_truth,
    ).sum()

    false_negative = np.logical_and(
        ~prediction,
        ground_truth,
    ).sum()

    denominator = (
        true_positive
        + false_negative
    )

    if denominator == 0:
        return 0.0

    return (
        true_positive
        / denominator
    )


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    print(
        "Loading DeepGlobe image..."
    )

    image = Image.open(
        IMAGE_PATH
    ).convert("RGB")

    print(
        "Image size:",
        image.size,
    )

    # -----------------------------------------------------
    # Ground truth
    # -----------------------------------------------------

    print(
        "\nDecoding ground-truth road mask..."
    )

    ground_truth = load_ground_truth(
        ANNOTATION_PATH,
        image.width,
        image.height,
    )

    ground_truth_pixels = int(
        ground_truth.sum()
    )

    print(
        "Ground-truth road pixels:",
        ground_truth_pixels,
    )

    print(
        "Ground-truth road percentage:",
        f"{ground_truth_pixels / ground_truth.size * 100:.3f}%",
    )

    # Save ground truth
    ground_truth_image = (
        ground_truth.astype(
            np.uint8
        )
        * 255
    )

    Image.fromarray(
        ground_truth_image
    ).save(
        OUTPUT_DIR
        / "ground_truth_roads.png"
    )

    # -----------------------------------------------------
    # SegFormer
    # -----------------------------------------------------

    print(
        "\nLoading OpenEarthMap SegFormer..."
    )

    predictor = (
        OpenEarthMapPredictor()
    )

    print(
        "\nRunning segmentation..."
    )

    result = predictor.predict(
        image
    )

    prediction = result.mask

    print(
        "Prediction shape:",
        prediction.shape,
    )

    # -----------------------------------------------------
    # Inspect predicted classes
    # -----------------------------------------------------

    classes, counts = np.unique(
        prediction,
        return_counts=True,
    )

    print(
        "\nPredicted class distribution:"
    )

    for class_id, count in zip(
        classes,
        counts,
    ):

        percentage = (
            count
            / prediction.size
            * 100
        )

        print(
            f"Class {class_id}: "
            f"{count} pixels "
            f"({percentage:.3f}%)"
        )

    # -----------------------------------------------------
    # Extract road class
    # -----------------------------------------------------

    predicted_roads = (
        prediction
        == predictor.ROAD_CLASS_ID
    )
    from app.engines.analysis.roads import RoadExtractor

    raw_road_mask = predicted_roads.astype(np.uint8)

    refined_road_mask = RoadExtractor.refine(
        raw_road_mask,
        min_component_size=50,
        kernel_size=5,
        closing_iterations=1,
    )
    raw_iou = calculate_iou(
        raw_road_mask,
        ground_truth,
    )

    raw_precision = calculate_precision(
        raw_road_mask,
        ground_truth,
    )

    raw_recall = calculate_recall(
        raw_road_mask,
        ground_truth,
    )

    refined_iou = calculate_iou(
        refined_road_mask,
        ground_truth,
    )

    refined_precision = calculate_precision(
        refined_road_mask,
        ground_truth,
    )

    refined_recall = calculate_recall(
        refined_road_mask,
        ground_truth,
    )
    print("\nRAW MASK")
    print(f"IoU:       {raw_iou:.4f}")
    print(f"Precision: {raw_precision:.4f}")
    print(f"Recall:    {raw_recall:.4f}")

    print("\nREFINED MASK")
    print(f"IoU:       {refined_iou:.4f}")
    print(f"Precision: {refined_precision:.4f}")
    print(f"Recall:    {refined_recall:.4f}")
    predicted_road_pixels = int(
        predicted_roads.sum()
    )
    Image.fromarray(
        refined_road_mask * 255
    ).save(
        OUTPUT_DIR / "refined_roads.png"
    )
    print(
        "\nPredicted road pixels:",
        predicted_road_pixels,
    )

    print(
        "Predicted road percentage:",
        f"{predicted_road_pixels / predicted_roads.size * 100:.3f}%",
    )

    # -----------------------------------------------------
    # Save prediction
    # -----------------------------------------------------

    predicted_image = (
        predicted_roads.astype(
            np.uint8
        )
        * 255
    )

    Image.fromarray(
        predicted_image
    ).save(
        OUTPUT_DIR
        / "predicted_roads.png"
    )

    # -----------------------------------------------------
    # Metrics
    # -----------------------------------------------------

    iou = calculate_iou(
        predicted_roads,
        ground_truth,
    )

    precision = calculate_precision(
        predicted_roads,
        ground_truth,
    )

    recall = calculate_recall(
        predicted_roads,
        ground_truth,
    )

    print(
        "\n================================"
    )

    print(
        "DEEPGLOBE VALIDATION RESULT"
    )

    print(
        "================================"
    )

    print(
        f"Model: {result.model_name}"
    )

    print(
        f"Inference: "
        f"{result.inference_time_ms:.2f} ms"
    )

    print(
        f"Ground-truth roads: "
        f"{ground_truth_pixels}"
    )

    print(
        f"Predicted roads: "
        f"{predicted_road_pixels}"
    )

    print(
        f"IoU: {iou:.4f}"
    )

    print(
        f"Precision: {precision:.4f}"
    )

    print(
        f"Recall: {recall:.4f}"
    )

    print(
        "\nGenerated:"
    )

    print(
        OUTPUT_DIR
        / "ground_truth_roads.png"
    )

    print(
        OUTPUT_DIR
        / "predicted_roads.png"
    )


if __name__ == "__main__":
    main()