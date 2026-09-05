from pathlib import Path
import json
import time

import numpy as np
from PIL import Image

from app.engines.vision.registry import ModelRegistry


# ============================================================
# CONFIG
# ============================================================

SPLIT_FILE = Path(
    "generated/deepglobe_split.json"
)

CACHE_DIR = Path(
    "generated/ensemble_cache"
)

# We only need a representative optimization subset.
# The previous 500-image experiment already established
# that D-LinkNet + RoadGIE is a useful candidate.
OPTIMIZATION_COUNT = 500

VALIDATION_COUNT = 200

TEST_COUNT = 300

SEED = 42


# ============================================================
# HELPERS
# ============================================================

def load_split():

    with open(
        SPLIT_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


def select_subset(
    pairs,
    count,
    seed,
):

    if len(pairs) <= count:

        return pairs

    rng = np.random.default_rng(
        seed
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


def extract_probability(
    result,
    model_name,
    image_size,
):

    if result.logits is None:

        raise RuntimeError(
            f"{model_name} did not return "
            "probability data."
        )

    probability = np.asarray(
        result.logits
    )

    if probability.ndim == 4:

        probability = probability[0]

    if model_name == "openearthmap":

        probability = probability[4]

    else:

        probability = np.squeeze(
            probability
        )

    if probability.ndim != 2:

        raise RuntimeError(
            f"{model_name} probability "
            f"shape is invalid: "
            f"{probability.shape}"
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
                (width, height),
                Image.Resampling.BILINEAR,
            ),
            dtype=np.float32,
        )

    return probability.astype(
        np.float32
    )


def load_ground_truth(
    mask_path,
):

    return (
        np.asarray(
            Image.open(
                mask_path
            ).convert("L")
        )
        > 127
    )


# ============================================================
# CACHE ONE SPLIT
# ============================================================

def cache_split(
    name,
    pairs,
    dlinknet,
    roadgie,
):

    output_dir = (
        CACHE_DIR / name
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    probability_file = (
        output_dir
        / "probabilities.npz"
    )

    if probability_file.exists():

        print()
        print(
            f"{name}: cache already exists."
        )

        print(
            f"Using: "
            f"{probability_file}"
        )

        return

    print()
    print("=" * 70)
    print(
        f"CACHING {name.upper()}"
    )
    print("=" * 70)

    dlink_maps = []
    roadgie_maps = []
    ground_truths = []

    start = time.perf_counter()

    for index, pair in enumerate(
        pairs,
        start=1,
    ):

        image_path = Path(
            pair["image"]
        )

        mask_path = Path(
            pair["mask"]
        )

        print(
            f"[{index}/{len(pairs)}] "
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
                "dlinknet34",
                image.size,
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
                "roadgie",
                image.size,
            )
        )

        dlink_maps.append(
            dlink_probability
        )

        roadgie_maps.append(
            roadgie_probability
        )

        ground_truths.append(
            ground_truth
        )

    elapsed = (
        time.perf_counter()
        - start
    )

    dlink_maps = np.stack(
        dlink_maps
    )

    roadgie_maps = np.stack(
        roadgie_maps
    )

    ground_truths = np.stack(
        ground_truths
    )

    np.savez_compressed(
        probability_file,
        dlink=dlink_maps,
        roadgie=roadgie_maps,
        ground_truth=ground_truths,
    )

    print()
    print(
        f"{name} cache complete."
    )

    print(
        f"D-LinkNet shape : "
        f"{dlink_maps.shape}"
    )

    print(
        f"RoadGIE shape    : "
        f"{roadgie_maps.shape}"
    )

    print(
        f"Ground truth     : "
        f"{ground_truths.shape}"
    )

    print(
        f"Elapsed          : "
        f"{elapsed:.2f} seconds"
    )

    print(
        f"Saved            : "
        f"{probability_file}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print(
        "ATLAS — ENSEMBLE PROBABILITY CACHE"
    )
    print("=" * 70)

    split = load_split()

    optimization_pairs = (
        select_subset(
            split["train"],
            OPTIMIZATION_COUNT,
            SEED,
        )
    )

    validation_pairs = (
        select_subset(
            split["validation"],
            VALIDATION_COUNT,
            SEED + 1,
        )
    )

    test_pairs = (
        select_subset(
            split["test"],
            TEST_COUNT,
            SEED + 2,
        )
    )

    print()
    print(
        "CACHE DATASET"
    )

    print(
        f"Optimization : "
        f"{len(optimization_pairs)}"
    )

    print(
        f"Validation   : "
        f"{len(validation_pairs)}"
    )

    print(
        f"Test         : "
        f"{len(test_pairs)}"
    )

    # --------------------------------------------------------
    # Load models once
    # --------------------------------------------------------

    print()
    print(
        "Loading D-LinkNet34..."
    )

    dlinknet = ModelRegistry.get(
        "dlinknet34"
    )

    print()
    print(
        "Loading RoadGIE..."
    )

    roadgie = ModelRegistry.get(
        "roadgie"
    )

    # --------------------------------------------------------
    # Cache
    # --------------------------------------------------------

    cache_split(
        "optimization",
        optimization_pairs,
        dlinknet,
        roadgie,
    )

    cache_split(
        "validation",
        validation_pairs,
        dlinknet,
        roadgie,
    )

    cache_split(
        "test",
        test_pairs,
        dlinknet,
        roadgie,
    )

    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    metadata = {
        "seed": SEED,
        "optimization_count":
            len(optimization_pairs),
        "validation_count":
            len(validation_pairs),
        "test_count":
            len(test_pairs),
        "models": [
            "dlinknet34",
            "roadgie",
        ],
        "source_split":
            str(
                SPLIT_FILE.resolve()
            ),
    }

    with open(
        CACHE_DIR / "metadata.json",
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metadata,
            file,
            indent=4,
        )

    print()
    print("=" * 70)
    print(
        "CACHE COMPLETE"
    )
    print("=" * 70)

    print(
        f"Cache directory: "
        f"{CACHE_DIR.resolve()}"
    )

    print()
    print(
        "Neural-network inference is now "
        "cached."
    )

    print(
        "Future weight/threshold searches "
        "will not rerun the models."
    )


if __name__ == "__main__":
    main()