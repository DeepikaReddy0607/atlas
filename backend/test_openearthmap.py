from transformers import (
    AutoImageProcessor,
    SegformerForSemanticSegmentation,
)

MODEL_NAME = "odil111/segformer-fine-tuned-on-openearthmap"

print("Loading processor...")

processor = AutoImageProcessor.from_pretrained(MODEL_NAME)

print("Loading model...")

model = SegformerForSemanticSegmentation.from_pretrained(MODEL_NAME)

print("SUCCESS!")

print(model.config)