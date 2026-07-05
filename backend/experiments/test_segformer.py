from transformers import SegformerImageProcessor, SegformerForSemanticSegmentation

MODEL_NAME = "nvidia/segformer-b0-finetuned-ade-512-512"

print("Loading processor...")
processor = SegformerImageProcessor.from_pretrained(MODEL_NAME)

print("Loading model...")
model = SegformerForSemanticSegmentation.from_pretrained(MODEL_NAME)

print("Model loaded successfully!")

print(f"Number of classes: {model.config.num_labels}")

print(model.config.id2label)