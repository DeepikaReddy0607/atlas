from pathlib import Path
import json

import numpy as np


DATASET_ROOT = Path(
    r"D:\Projects\atlas\datasets\DeepGlobe"
)

TRAIN_DIR = DATASET_ROOT / "train"

OUTPUT = Path(
    "generated/deepglobe_split.json"
)

SEED = 42

TRAIN_RATIO = 0.70
VALID_RATIO = 0.15
TEST_RATIO = 0.15


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
                {
                    "id": image_id,
                    "image": str(
                        image_path.resolve()
                    ),
                    "mask": str(
                        mask_path.resolve()
                    ),
                }
            )

    return pairs


def main():

    print("=" * 70)
    print(
        "ATLAS — DEEPGLOBE SPLIT CREATION"
    )
    print("=" * 70)

    pairs = find_pairs()

    print(
        f"Labeled pairs found: "
        f"{len(pairs)}"
    )

    if len(pairs) < 100:

        raise RuntimeError(
            "Too few labeled pairs found."
        )

    rng = np.random.default_rng(
        SEED
    )

    indices = np.arange(
        len(pairs)
    )

    rng.shuffle(indices)

    total = len(indices)

    train_end = int(
        total * TRAIN_RATIO
    )

    valid_end = (
        train_end
        + int(
            total * VALID_RATIO
        )
    )

    train_indices = indices[
        :train_end
    ]

    valid_indices = indices[
        train_end:valid_end
    ]

    test_indices = indices[
        valid_end:
    ]

    train_pairs = [
        pairs[i]
        for i in train_indices
    ]

    valid_pairs = [
        pairs[i]
        for i in valid_indices
    ]

    test_pairs = [
        pairs[i]
        for i in test_indices
    ]

    # --------------------------------------------------------
    # Safety checks
    # --------------------------------------------------------

    train_ids = {
        item["id"]
        for item in train_pairs
    }

    valid_ids = {
        item["id"]
        for item in valid_pairs
    }

    test_ids = {
        item["id"]
        for item in test_pairs
    }

    assert train_ids.isdisjoint(
        valid_ids
    )

    assert train_ids.isdisjoint(
        test_ids
    )

    assert valid_ids.isdisjoint(
        test_ids
    )

    assert (
        len(train_ids)
        + len(valid_ids)
        + len(test_ids)
        == total
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    split = {
        "dataset": "DeepGlobe",
        "seed": SEED,
        "source": str(
            TRAIN_DIR.resolve()
        ),
        "total": total,
        "train": train_pairs,
        "validation": valid_pairs,
        "test": test_pairs,
    }

    with open(
        OUTPUT,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            split,
            f,
            indent=2,
        )

    print()
    print(
        "SPLIT CREATED"
    )
    print("-" * 70)

    print(
        f"Optimization : "
        f"{len(train_pairs)}"
    )

    print(
        f"Validation   : "
        f"{len(valid_pairs)}"
    )

    print(
        f"Final test   : "
        f"{len(test_pairs)}"
    )

    print(
        f"Total        : "
        f"{total}"
    )

    print()
    print(
        f"Saved to: {OUTPUT.resolve()}"
    )

    print()
    print(
        "All split-overlap checks: PASS"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()