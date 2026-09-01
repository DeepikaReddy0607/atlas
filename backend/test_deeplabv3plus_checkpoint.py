from app.engines.vision.models.deeplabv3plus import (
    DeepLabV3PlusPredictor,
)


def main():

    print("=" * 60)
    print(
        "DEEPLABV3+ CHECKPOINT TEST"
    )
    print("=" * 60)

    predictor = (
        DeepLabV3PlusPredictor()
    )

    print()
    print(
        "CHECKPOINT COMPATIBILITY: PASS"
    )
    print(
        "MODEL READY"
    )


if __name__ == "__main__":
    main()