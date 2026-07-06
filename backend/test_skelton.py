import cv2

from app.engines.analysis.skeleton import Skeletonizer

# Load ground-truth road mask
mask = cv2.imread(
    "data/sample/roads_gt.png",
    cv2.IMREAD_GRAYSCALE,
)

# Generate skeleton
skeleton = Skeletonizer.build(mask)

# Save result
cv2.imwrite(
    "data/sample/skeleton.png",
    skeleton * 255,
)

print("Skeleton generated successfully!")