import json
import time
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from app.engines.vision.registry import ModelRegistry
from app.engines.analysis.skeleton import Skeletonizer
from app.engines.analysis.graph_builder import GraphBuilder
from app.engines.analysis.topology import TopologyBuilder


# ============================================================
# CONFIGURATION
# ============================================================

DATASET_ROOT = Path(
    r"D:\Projects\atlas\datasets\DeepGlobe"
)

TRAIN_DIR = DATASET_ROOT / "train"

SPLIT_FILE = Path(
    "generated/deepglobe_split.json"
)

NUM_IMAGES = 20
SEED = 42

DLINK_THRESHOLD = 0.5

ENSEMBLE_DLINK_WEIGHT = 0.65
ENSEMBLE_ROADGIE_WEIGHT = 0.35
ENSEMBLE_THRESHOLD = 0.275


# ============================================================
# LOAD SPLIT
# ============================================================
def calculate_skeleton_metrics(
    predicted_skeleton,
    ground_truth_skeleton,
):
    pred = (
        predicted_skeleton > 0
    )

    gt = (
        ground_truth_skeleton > 0
    )

    intersection = np.logical_and(
        pred,
        gt,
    ).sum()

    pred_pixels = pred.sum()
    gt_pixels = gt.sum()

    union = np.logical_or(
        pred,
        gt,
    ).sum()

    iou = (
        intersection / union
        if union > 0
        else 1.0
    )

    dice = (
        2.0 * intersection
        /
        (
            pred_pixels
            + gt_pixels
        )
        if (
            pred_pixels
            + gt_pixels
        ) > 0
        else 1.0
    )

    precision = (
        intersection / pred_pixels
        if pred_pixels > 0
        else 0.0
    )

    recall = (
        intersection / gt_pixels
        if gt_pixels > 0
        else 0.0
    )

    return {
        "skeleton_iou": float(iou),
        "skeleton_dice": float(dice),
        "skeleton_precision": float(
            precision
        ),
        "skeleton_recall": float(
            recall
        ),
    }

def calculate_tolerant_skeleton_metrics(
    predicted_skeleton,
    ground_truth_skeleton,
    tolerance=3,
):
    """
    Evaluate skeleton agreement with spatial tolerance.

    A predicted skeleton pixel is considered correct if a
    ground-truth skeleton pixel exists within `tolerance` pixels.

    Likewise, a ground-truth skeleton pixel is considered
    recovered if a predicted skeleton pixel exists within the
    same tolerance.
    """

    pred = (
        predicted_skeleton > 0
    ).astype(np.uint8)

    gt = (
        ground_truth_skeleton > 0
    ).astype(np.uint8)

    # --------------------------------------------------------
    # Distance from every pixel to the nearest skeleton pixel.
    #
    # cv2.distanceTransform computes distance to zero-valued
    # pixels, so invert the skeleton masks.
    # --------------------------------------------------------

    pred_distance = cv2.distanceTransform(
        1 - pred,
        cv2.DIST_L2,
        3,
    )

    gt_distance = cv2.distanceTransform(
        1 - gt,
        cv2.DIST_L2,
        3,
    )

    # --------------------------------------------------------
    # Precision:
    # predicted skeleton pixels that are close to GT.
    # --------------------------------------------------------

    pred_count = int(
        pred.sum()
    )

    if pred_count > 0:

        matched_pred = (
            pred_distance[pred > 0]
            <= tolerance
        )

        precision = (
            matched_pred.sum()
            / pred_count
        )

    else:

        precision = 0.0

    # --------------------------------------------------------
    # Recall:
    # GT skeleton pixels recovered by prediction.
    # --------------------------------------------------------

    gt_count = int(
        gt.sum()
    )

    if gt_count > 0:

        matched_gt = (
            gt_distance[gt > 0]
            <= tolerance
        )

        recall = (
            matched_gt.sum()
            / gt_count
        )

    else:

        recall = 0.0

    # --------------------------------------------------------
    # F1
    # --------------------------------------------------------

    if (
        precision + recall
    ) > 0:

        f1 = (
            2.0
            * precision
            * recall
            /
            (
                precision
                + recall
            )
        )

    else:

        f1 = 0.0

    return {
        "skeleton_precision":
            float(precision),

        "skeleton_recall":
            float(recall),

        "skeleton_f1":
            float(f1),

        "tolerance":
            tolerance,
    }

def load_test_pairs():

    with open(
        SPLIT_FILE,
        "r",
        encoding="utf-8",
    ) as f:

        split = json.load(f)

    # The generated split uses the final test subset.
    test_items = split["test"]

    pairs = []

    for item in test_items:

        if isinstance(item, str):

            image_name = item

        else:

            image_name = (
                item.get("image")
                or item.get("image_name")
                or item.get("filename")
            )

        if image_name is None:
            continue

        image_path = (
            TRAIN_DIR / image_name
        )

        mask_name = (
            image_name
            .replace(
                "_sat.jpg",
                "_mask.png",
            )
            .replace(
                "_sat.png",
                "_mask.png",
            )
        )

        mask_path = (
            TRAIN_DIR / mask_name
        )

        if (
            image_path.exists()
            and mask_path.exists()
        ):

            pairs.append(
                (
                    image_path,
                    mask_path,
                )
            )

    if not pairs:

        raise RuntimeError(
            "No labeled test pairs found."
        )

    rng = np.random.default_rng(
        SEED
    )

    count = min(
        NUM_IMAGES,
        len(pairs),
    )

    indices = rng.choice(
        len(pairs),
        size=count,
        replace=False,
    )

    indices.sort()

    return [
        pairs[i]
        for i in indices
    ]


# ============================================================
# PROBABILITY EXTRACTION
# ============================================================

def extract_probability(
    result,
    image_size,
):

    logits = getattr(
        result,
        "logits",
        None,
    )

    if logits is None:

        raise RuntimeError(
            f"{result.model_name} "
            "did not return logits."
        )

    probability = np.asarray(
        logits
    )

    if probability.ndim == 4:

        probability = probability[0]

    probability = np.squeeze(
        probability
    )

    if (
        probability.min() < 0.0
        or probability.max() > 1.0
    ):

        probability = (
            1.0
            /
            (
                1.0
                + np.exp(
                    -probability
                )
            )
        )

    if probability.ndim != 2:

        raise RuntimeError(
            f"Unexpected probability "
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

    return probability


# ============================================================
# TOPOLOGY ANALYSIS
# ============================================================

def analyze_topology(mask):

    binary = (
        mask > 0
    ).astype(
        np.uint8
    ) * 255

    # --------------------------------------------------------
    # Connected components
    # --------------------------------------------------------

    (
        component_count,
        labels,
        stats,
        centroids,
    ) = cv2.connectedComponentsWithStats(
        binary,
        connectivity=8,
    )

    component_sizes = stats[
        1:,
        cv2.CC_STAT_AREA,
    ]

    total_road_pixels = int(
        component_sizes.sum()
    )

    if len(component_sizes) > 0:

        largest_component = int(
            component_sizes.max()
        )

    else:

        largest_component = 0

    largest_component_ratio = (
        largest_component
        / total_road_pixels
        if total_road_pixels > 0
        else 0.0
    )

    connected_components = max(
        0,
        component_count - 1,
    )

    # --------------------------------------------------------
    # ATLAS graph pipeline
    # --------------------------------------------------------

    skeleton = Skeletonizer.build(
        binary
    )

    pixel_graph = GraphBuilder.build(
        skeleton
    )

    topology = TopologyBuilder.build(
        pixel_graph
    )

    skeleton_pixels = int(
        np.count_nonzero(
            skeleton
        )
    )

    topology_nodes = int(
        topology.number_of_nodes()
    )

    topology_edges = int(
        topology.number_of_edges()
    )

    degrees = [
        degree
        for _, degree
        in topology.degree()
    ]

    dead_ends = sum(
        degree == 1
        for degree in degrees
    )

    junctions = sum(
        degree >= 3
        for degree in degrees
    )

    isolated_nodes = sum(
        degree == 0
        for degree in degrees
    )

    return {
        "road_pixels":
            total_road_pixels,

        "connected_components":
            connected_components,

        "largest_component_ratio":
            largest_component_ratio,

        "skeleton_pixels":
            skeleton_pixels,

        "pixel_graph_nodes":
            pixel_graph.number_of_nodes(),

        "pixel_graph_edges":
            pixel_graph.number_of_edges(),

        "topology_nodes":
            topology_nodes,

        "topology_edges":
            topology_edges,

        "dead_ends":
            dead_ends,

        "junctions":
            junctions,

        "isolated_nodes":
            isolated_nodes,
    }


# ============================================================
# MASK METRICS
# ============================================================

def calculate_segmentation_metrics(
    prediction,
    ground_truth,
):

    prediction = prediction.astype(
        bool
    )

    ground_truth = ground_truth.astype(
        bool
    )

    intersection = np.logical_and(
        prediction,
        ground_truth,
    ).sum()

    union = np.logical_or(
        prediction,
        ground_truth,
    ).sum()

    pred_pixels = prediction.sum()
    gt_pixels = ground_truth.sum()

    iou = (
        intersection / union
        if union > 0
        else 1.0
    )

    dice = (
        2.0 * intersection
        /
        (
            pred_pixels
            + gt_pixels
        )
        if (
            pred_pixels
            + gt_pixels
        ) > 0
        else 1.0
    )

    return float(iou), float(dice)


# ============================================================
# GROUND TRUTH
# ============================================================

def load_ground_truth(
    mask_path,
    target_size,
):

    mask = cv2.imread(
        str(mask_path),
        cv2.IMREAD_GRAYSCALE,
    )

    if mask is None:

        raise RuntimeError(
            f"Could not load "
            f"{mask_path}"
        )

    if mask.shape != (
        target_size[1],
        target_size[0],
    ):

        mask = cv2.resize(
            mask,
            target_size,
            interpolation=cv2.INTER_NEAREST,
        )

    # DeepGlobe road masks are non-zero for road.
    return mask > 0


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print(
        "ATLAS — TOPOLOGY BENCHMARK"
    )
    print("=" * 70)

    print(
        f"Images: {NUM_IMAGES}"
    )

    print(
        "D-LinkNet threshold : "
        f"{DLINK_THRESHOLD}"
    )

    print(
        "Ensemble weights    : "
        f"{ENSEMBLE_DLINK_WEIGHT:.2f} / "
        f"{ENSEMBLE_ROADGIE_WEIGHT:.2f}"
    )

    print(
        "Ensemble threshold  : "
        f"{ENSEMBLE_THRESHOLD}"
    )

    print()

    pairs = load_test_pairs()

    print(
        f"Selected images: "
        f"{len(pairs)}"
    )

    # --------------------------------------------------------
    # Load models once.
    # --------------------------------------------------------

    print()
    print("Loading D-LinkNet34...")

    dlinknet = ModelRegistry.get(
        "dlinknet34"
    )

    print(
        "D-LinkNet34 ready."
    )

    print()
    print("Loading RoadGIE...")

    roadgie = ModelRegistry.get(
        "roadgie"
    )

    print(
        "RoadGIE ready."
    )

    # --------------------------------------------------------
    # Accumulators
    # --------------------------------------------------------

    dlink_topology_results = []
    ensemble_topology_results = []

    dlink_skeleton_results = []
    ensemble_skeleton_results = []

    dlink_tolerant_skeleton_results = []
    ensemble_tolerant_skeleton_results = []

    dlink_ious = []
    dlink_dices = []

    ensemble_ious = []
    ensemble_dices = []

    # --------------------------------------------------------
    # Evaluation
    # --------------------------------------------------------

    total_start = time.perf_counter()

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

        image_size = image.size

        # ----------------------------------------------------
        # D-LinkNet
        # ----------------------------------------------------

        dlink_result = (
            dlinknet.predict(
                image
            )
        )

        dlink_probability = (
            extract_probability(
                dlink_result,
                image_size,
            )
        )

        # ----------------------------------------------------
        # RoadGIE
        # ----------------------------------------------------

        roadgie_result = (
            roadgie.predict(
                image
            )
        )

        roadgie_probability = (
            extract_probability(
                roadgie_result,
                image_size,
            )
        )

               # ----------------------------------------------------
        # Predictions
        # ----------------------------------------------------

        # D-LinkNet probability
        dlink_probability = (
            extract_probability(
                dlink_result,
                image_size,
            )
        )

        # RoadGIE probability
        roadgie_probability = (
            extract_probability(
                roadgie_result,
                image_size,
            )
        )

        # ----------------------------------------------------
        # D-LinkNet mask
        # ----------------------------------------------------

        dlink_mask = (
            dlink_probability
            >= DLINK_THRESHOLD
        )

        # ----------------------------------------------------
        # Ensemble probability
        # ----------------------------------------------------

        ensemble_probability = (
            ENSEMBLE_DLINK_WEIGHT
            * dlink_probability
            +
            ENSEMBLE_ROADGIE_WEIGHT
            * roadgie_probability
        )

        # ----------------------------------------------------
        # Ensemble mask
        # ----------------------------------------------------

        ensemble_mask = (
            ensemble_probability
            >= ENSEMBLE_THRESHOLD
        )

        # ----------------------------------------------------
        # Ground truth
        # ----------------------------------------------------

        ground_truth = (
            load_ground_truth(
                mask_path,
                image_size,
            )
        )

        ground_truth_binary = (
            ground_truth.astype(
                np.uint8
            )
            * 255
        )

        ground_truth_skeleton = (
            Skeletonizer.build(
                ground_truth_binary
            )
        )

        # ----------------------------------------------------
        # Prediction skeletons
        # ----------------------------------------------------

        dlink_skeleton = (
            Skeletonizer.build(
                dlink_mask.astype(
                    np.uint8
                ) * 255
            )
        )

        ensemble_skeleton = (
            Skeletonizer.build(
                ensemble_mask.astype(
                    np.uint8
                ) * 255
            )
        )

        # ----------------------------------------------------
        # Ground-truth skeleton metrics
        # ----------------------------------------------------

        dlink_skeleton_metrics = (
            calculate_skeleton_metrics(
                dlink_skeleton,
                ground_truth_skeleton,
            )
        )

        ensemble_skeleton_metrics = (
            calculate_skeleton_metrics(
                ensemble_skeleton,
                ground_truth_skeleton,
            )
        )

        dlink_skeleton_results.append(
            dlink_skeleton_metrics
        )

        ensemble_skeleton_results.append(
            ensemble_skeleton_metrics
        )

        # ----------------------------------------------------
        # Ground truth
        # ----------------------------------------------------

        ground_truth = (
            load_ground_truth(
                mask_path,
                image_size,
            )
        )

        ground_truth_binary = (
            ground_truth.astype(
                np.uint8
            )
            * 255
        )

        ground_truth_skeleton = (
            Skeletonizer.build(
                ground_truth_binary
            )
        )
        dlink_tolerant_metrics = (
            calculate_tolerant_skeleton_metrics(
                dlink_skeleton,
                ground_truth_skeleton,
                tolerance=3,
            )
        )

        ensemble_tolerant_metrics = (
            calculate_tolerant_skeleton_metrics(
                ensemble_skeleton,
                ground_truth_skeleton,
                tolerance=3,
            )
        )

        dlink_tolerant_skeleton_results.append(
            dlink_tolerant_metrics
        )

        ensemble_tolerant_skeleton_results.append(
            ensemble_tolerant_metrics
        )
        # ----------------------------------------------------
        # Segmentation metrics
        # ----------------------------------------------------

        dlink_iou, dlink_dice = (
            calculate_segmentation_metrics(
                dlink_mask,
                ground_truth,
            )
        )

        ensemble_iou, ensemble_dice = (
            calculate_segmentation_metrics(
                ensemble_mask,
                ground_truth,
            )
        )

        dlink_ious.append(
            dlink_iou
        )

        dlink_dices.append(
            dlink_dice
        )

        ensemble_ious.append(
            ensemble_iou
        )

        ensemble_dices.append(
            ensemble_dice
        )

        # ----------------------------------------------------
        # Topology
        # ----------------------------------------------------

        dlink_metrics = (
            analyze_topology(
                dlink_mask
            )
        )

        ensemble_metrics = (
            analyze_topology(
                ensemble_mask
            )
        )

        dlink_topology_results.append(
            dlink_metrics
        )

        ensemble_topology_results.append(
            ensemble_metrics
        )

        print(
            f"  D-LinkNet "
            f"IoU={dlink_iou:.4f} "
            f"components="
            f"{dlink_metrics['connected_components']} "
            f"topo_edges="
            f"{dlink_metrics['topology_edges']}"
        )

        print(
            f"  Ensemble  "
            f"IoU={ensemble_iou:.4f} "
            f"components="
            f"{ensemble_metrics['connected_components']} "
            f"topo_edges="
            f"{ensemble_metrics['topology_edges']}"
        )

    elapsed = (
        time.perf_counter()
        - total_start
    )

    # ========================================================
    # AGGREGATION
    # ========================================================

    def average_metric(
        results,
        key,
    ):

        return float(
            np.mean(
                [
                    item[key]
                    for item in results
                ]
            )
        )

    print()
    print("=" * 70)
    print(
        "SEGMENTATION COMPARISON"
    )
    print("=" * 70)

    print(
        f"D-LinkNet IoU : "
        f"{np.mean(dlink_ious):.4f}"
    )

    print(
        f"Ensemble IoU  : "
        f"{np.mean(ensemble_ious):.4f}"
    )

    print(
        f"IoU change    : "
        f"{np.mean(ensemble_ious) - np.mean(dlink_ious):+.4f}"
    )

    print()

    print(
        f"D-LinkNet Dice: "
        f"{np.mean(dlink_dices):.4f}"
    )

    print(
        f"Ensemble Dice : "
        f"{np.mean(ensemble_dices):.4f}"
    )

    print(
        f"Dice change   : "
        f"{np.mean(ensemble_dices) - np.mean(dlink_dices):+.4f}"
    )

    # ========================================================
    # TOPOLOGY COMPARISON
    # ========================================================

    metrics_to_compare = [
        (
            "road_pixels",
            "Road pixels",
        ),
        (
            "connected_components",
            "Connected components",
        ),
        (
            "largest_component_ratio",
            "Largest component ratio",
        ),
        (
            "skeleton_pixels",
            "Skeleton pixels",
        ),
        (
            "pixel_graph_nodes",
            "Pixel graph nodes",
        ),
        (
            "pixel_graph_edges",
            "Pixel graph edges",
        ),
        (
            "topology_nodes",
            "Topology nodes",
        ),
        (
            "topology_edges",
            "Topology edges",
        ),
        (
            "dead_ends",
            "Dead ends",
        ),
        (
            "junctions",
            "Junctions",
        ),
        (
            "isolated_nodes",
            "Isolated nodes",
        ),
    ]

    print()
    print("=" * 70)
    print(
        "ATLAS TOPOLOGY COMPARISON"
    )
    print("=" * 70)

    print(
        f"{'Metric':30s}"
        f"{'D-LinkNet':>15s}"
        f"{'Ensemble':>15s}"
        f"{'Change':>15s}"
    )

    print("-" * 70)

    for key, label in metrics_to_compare:

        dlink_value = average_metric(
            dlink_topology_results,
            key,
        )

        ensemble_value = average_metric(
            ensemble_topology_results,
            key,
        )

        change = (
            ensemble_value
            - dlink_value
        )

        if (
            "ratio" in key
        ):

            print(
                f"{label:30s}"
                f"{dlink_value:15.4f}"
                f"{ensemble_value:15.4f}"
                f"{change:+15.4f}"
            )

        else:

            print(
                f"{label:30s}"
                f"{dlink_value:15.2f}"
                f"{ensemble_value:15.2f}"
                f"{change:+15.2f}"
            )

    print("-" * 70)

    print(
        f"Evaluation time: "
        f"{elapsed / 60:.2f} minutes"
    )

    print()
    print(
        "TOPOLOGY BENCHMARK COMPLETE"
    )
    print("=" * 70)

    print()
    print("=" * 70)
    print(
        "GROUND-TRUTH SKELETON COMPARISON"
    )
    print("=" * 70)

    print(
        f"{'Metric':30s}"
        f"{'D-LinkNet':>15s}"
        f"{'Ensemble':>15s}"
        f"{'Change':>15s}"
    )

    print("-" * 70)

    for key, label in [
        (
            "skeleton_iou",
            "Skeleton IoU",
        ),
        (
            "skeleton_dice",
            "Skeleton Dice",
        ),
        (
            "skeleton_precision",
            "Skeleton Precision",
        ),
        (
            "skeleton_recall",
            "Skeleton Recall",
        ),
    ]:

        dlink_value = np.mean(
            [
                item[key]
                for item
                in dlink_skeleton_results
            ]
        )

        ensemble_value = np.mean(
            [
                item[key]
                for item
                in ensemble_skeleton_results
            ]
        )

        change = (
            ensemble_value
            - dlink_value
        )

        print(
            f"{label:30s}"
            f"{dlink_value:15.4f}"
            f"{ensemble_value:15.4f}"
            f"{change:+15.4f}"
        )

    print("-" * 70)

    print()
    print("=" * 70)
    print(
        "TOLERANT SKELETON COMPARISON "
        "(3 PIXELS)"
    )
    print("=" * 70)

    print(
        f"{'Metric':30s}"
        f"{'D-LinkNet':>15s}"
        f"{'Ensemble':>15s}"
        f"{'Change':>15s}"
    )

    print("-" * 70)

    for key, label in [
        (
            "skeleton_precision",
            "Skeleton Precision @3",
        ),
        (
            "skeleton_recall",
            "Skeleton Recall @3",
        ),
        (
            "skeleton_f1",
            "Skeleton F1 @3",
        ),
    ]:

        dlink_value = np.mean(
            [
                item[key]
                for item
                in dlink_tolerant_skeleton_results
            ]
        )

        ensemble_value = np.mean(
            [
                item[key]
                for item
                in ensemble_tolerant_skeleton_results
            ]
        )

        print(
            f"{label:30s}"
            f"{dlink_value:15.4f}"
            f"{ensemble_value:15.4f}"
            f"{ensemble_value - dlink_value:+15.4f}"
        )

    print("-" * 70)
if __name__ == "__main__":
    main()