from app.engines.vision.pipeline import VisionPipeline
from outputs.visualizations.engine import VisualizationEngine

image_path = "generated/tile0.png"   # use an image that exists

# Run the vision pipeline
vision = VisionPipeline("ade20k")
segmentation = vision.run(image_path)

# Generate overlay
visualizer = VisualizationEngine()

output_path = visualizer.generate_segmentation_overlay(
    image_path,
    segmentation,
)

print(output_path)