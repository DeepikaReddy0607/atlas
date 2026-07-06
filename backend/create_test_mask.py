import cv2
import numpy as np

# Create black canvas
img = np.zeros((512, 512), dtype=np.uint8)

# Horizontal road
cv2.line(img, (50, 256), (462, 256), 255, 8)

# Vertical road
cv2.line(img, (256, 50), (256, 462), 255, 8)

# Diagonal road
cv2.line(img, (320, 320), (470, 470), 255, 8)

# Dead-end road
cv2.line(img, (120, 120), (220, 180), 255, 8)

cv2.imwrite("data/sample/roads_gt.png", img)

print("Road mask created successfully!")