import time
import numpy as np
import torch
from PIL import Image
from transformers import (
    SegformerConfig,
    SegformerForSemanticSegmentation,
    SegformerImageProcessor,
)

from app.engines.vision.models.base import BasePredictor
from app.engines.vision.result import SegmentationResult


class OpenEarthMapPredictor(BasePredictor):

    MODEL_NAME = "OpenEarthMap-SegFormer-B5"

    CHECKPOINT_PATH = (
        "models/openearthmap/"
        "segformer_sem_seg_2024-05-16--14-40-45/"
        "segformer_sem_seg_checkpoint_epoch35.pt"
    )

    ROAD_CLASS_ID = 4
    NUM_CLASSES = 9

    def __init__(self):

        print(
            "Loading OpenEarthMap SegFormer-B5..."
        )

        # -----------------------------------------------------
        # Exact configuration recovered from checkpoint
        # -----------------------------------------------------

        config = SegformerConfig(
            num_labels=self.NUM_CLASSES,

            hidden_sizes=[
                64,
                128,
                320,
                512,
            ],

            depths=[
                3,
                4,
                6,
                3,
            ],

            num_attention_heads=[
                1,
                2,
                5,
                8,
            ],

            sr_ratios=[
                8,
                4,
                2,
                1,
            ],

            patch_sizes=[
                7,
                3,
                3,
                3,
            ],

            strides=[
                4,
                2,
                2,
                2,
            ],

            mlp_ratios=[
                4,
                4,
                4,
                4,
            ],

            decoder_hidden_size=768,

            semantic_loss_ignore_index=255,

            reshape_last_stage=True,
        )

        # -----------------------------------------------------
        # Create model
        # -----------------------------------------------------

        self.model = SegformerForSemanticSegmentation(
            config
        )

        # -----------------------------------------------------
        # Load checkpoint
        # -----------------------------------------------------

        print(
            "Loading OpenEarthMap checkpoint..."
        )

        checkpoint = torch.load(
            self.CHECKPOINT_PATH,
            map_location="cpu",
        )

        # Store checkpoint information on the instance.
        # This allows predict() to use it later.
        self.checkpoint_epoch = checkpoint.get(
            "epoch"
        )

        state_dict = checkpoint[
            "model_state_dict"
        ]

        # -----------------------------------------------------
        # Load model weights
        # -----------------------------------------------------

        missing_keys, unexpected_keys = (
            self.model.load_state_dict(
                state_dict,
                strict=False,
            )
        )

        # -----------------------------------------------------
        # Validate checkpoint
        # -----------------------------------------------------

        if missing_keys:
            print(
                "\nWARNING: Missing keys:"
            )

            for key in missing_keys:
                print(
                    f"  {key}"
                )

        if unexpected_keys:
            print(
                "\nWARNING: Unexpected keys:"
            )

            for key in unexpected_keys:
                print(
                    f"  {key}"
                )

        if (
            not missing_keys
            and not unexpected_keys
        ):
            print(
                "OpenEarthMap checkpoint "
                "loaded successfully."
            )
        else:
            raise RuntimeError(
                "OpenEarthMap SegFormer checkpoint "
                "does not match the configured "
                "SegFormer architecture."
            )

        self.model.eval()

        # -----------------------------------------------------
        # Image processor
        # -----------------------------------------------------

        self.processor = SegformerImageProcessor(
            do_resize=True,
            size={
                "height": 1000,
                "width": 1000,
            },
            do_rescale=True,
            rescale_factor=1 / 255,
            do_normalize=True,
            image_mean=[
                0.485,
                0.456,
                0.406,
            ],
            image_std=[
                0.229,
                0.224,
                0.225,
            ],
        )

        print(
            "OpenEarthMap SegFormer-B5 ready."
        )

    def predict(
        self,
        image: Image.Image,
    ) -> SegmentationResult:

        start = time.perf_counter()

        # -----------------------------------------------------
        # Ensure RGB
        # -----------------------------------------------------

        image = image.convert("RGB")

        original_size = image.size

        # -----------------------------------------------------
        # Preprocess
        # -----------------------------------------------------

        inputs = self.processor(
            images=image,
            return_tensors="pt",
        )

        # -----------------------------------------------------
        # Inference
        # -----------------------------------------------------

        with torch.no_grad():

            outputs = self.model(
                **inputs
            )

        # -----------------------------------------------------
        # Resize logits to original tile size
        # -----------------------------------------------------

        resized_logits = torch.nn.functional.interpolate(
            outputs.logits,
            size=(
                original_size[1],
                original_size[0],
            ),
            mode="bilinear",
            align_corners=False,
        )

        # -----------------------------------------------------
        # Convert logits to NumPy
        # -----------------------------------------------------

        logits = resized_logits[0].cpu().numpy()

        # -----------------------------------------------------
        # Local prediction
        #
        # Kept for compatibility/debugging.
        # The VisionPipeline will perform the final
        # argmax after stitching overlapping tiles.
        # -----------------------------------------------------

        prediction = np.argmax(
                logits,
                axis=0,
            ).astype(np.uint8)

        unique, counts = np.unique(
        prediction,
        return_counts=True,
        )

        print(
            "Predicted classes:",
            dict(zip(unique.tolist(), counts.tolist()))
        )
        # -----------------------------------------------------
        # Inference time
        # -----------------------------------------------------

        inference_time = (
            time.perf_counter()
            - start
        ) * 1000

        # -----------------------------------------------------
        # Return ATLAS SegmentationResult
        # -----------------------------------------------------

        return SegmentationResult(
            mask=prediction,
            model_name=self.MODEL_NAME,
            inference_time_ms=round(
                inference_time,
                2,
            ),
            image_size=original_size,
            metadata={
                "model_id": self.CHECKPOINT_PATH,
                "dataset": "OpenEarthMap",
                "architecture": "SegFormer-B5",
                "num_classes": self.NUM_CLASSES,
                "road_class_id": self.ROAD_CLASS_ID,
                "checkpoint_epoch": self.checkpoint_epoch,
            },
            logits=logits,
        )