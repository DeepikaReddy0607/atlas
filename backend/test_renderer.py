import cv2

from app.engines.visualization.renderer import GraphRenderer

canvas = GraphRenderer.blank()

cv2.imwrite(
    "generated/canvas.png",
    canvas,
)

print("Canvas created.")