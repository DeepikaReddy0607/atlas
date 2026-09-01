from app.engines.vision.models.roadgie import (
    RoadGIEPredictor,
)


def main():

    print("=" * 60)
    print("ROADGIE ATLAS CHECKPOINT TEST")
    print("=" * 60)

    predictor = RoadGIEPredictor()

    print()
    print("CHECKPOINT COMPATIBILITY: PASS")
    print("MODEL READY")


if __name__ == "__main__":
    main()