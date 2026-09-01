import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from torchvision.models import ResNet34_Weights, resnet34

from app.engines.vision.models.base import BasePredictor
from app.engines.vision.result import SegmentationResult


# ============================================================
# Decoder Block
# ============================================================

class DecoderBlock(nn.Module):
    """
    D-LinkNet / LinkNet decoder block.

    This structure matches the original trained checkpoint.
    """

    def __init__(
        self,
        in_channels: int,
        middle_channels: int,
        out_channels: int,
    ):
        super().__init__()

        self.conv1 = nn.Conv2d(
            in_channels,
            middle_channels,
            kernel_size=1,
            bias=True,
        )

        self.norm1 = nn.BatchNorm2d(
            middle_channels
        )

        self.deconv2 = nn.ConvTranspose2d(
            middle_channels,
            middle_channels,
            kernel_size=3,
            stride=2,
            padding=1,
            output_padding=1,
            bias=True,
        )

        self.norm2 = nn.BatchNorm2d(
            middle_channels
        )

        self.conv3 = nn.Conv2d(
            middle_channels,
            out_channels,
            kernel_size=1,
            bias=True,
        )

        self.norm3 = nn.BatchNorm2d(
            out_channels
        )

        self.relu = nn.ReLU(inplace=True)

    def forward(self, x):

        x = self.conv1(x)
        x = self.norm1(x)
        x = self.relu(x)

        x = self.deconv2(x)
        x = self.norm2(x)
        x = self.relu(x)

        x = self.conv3(x)
        x = self.norm3(x)
        x = self.relu(x)

        return x


# ============================================================
# Dilated Center Block
# ============================================================

class Dblock(nn.Module):
    """
    Dilated convolution block used by D-LinkNet.

    Four progressively dilated convolutions increase the
    receptive field while preserving spatial resolution.
    """

    def __init__(self, channel: int):
        super().__init__()

        self.dilate1 = nn.Conv2d(
            channel,
            channel,
            kernel_size=3,
            padding=1,
            dilation=1,
        )

        self.dilate2 = nn.Conv2d(
            channel,
            channel,
            kernel_size=3,
            padding=2,
            dilation=2,
        )

        self.dilate3 = nn.Conv2d(
            channel,
            channel,
            kernel_size=3,
            padding=4,
            dilation=4,
        )

        self.dilate4 = nn.Conv2d(
            channel,
            channel,
            kernel_size=3,
            padding=8,
            dilation=8,
        )

        self.relu = nn.ReLU(
            inplace=True
        )

    def forward(self, x):

        d1 = self.relu(
            self.dilate1(x)
        )

        d2 = self.relu(
            self.dilate2(d1)
        )

        d3 = self.relu(
            self.dilate3(d2)
        )

        d4 = self.relu(
            self.dilate4(d3)
        )

        return x + d1 + d2 + d3 + d4


# ============================================================
# D-LinkNet34
# ============================================================

class DLinkNet34(nn.Module):
    """
    Modern PyTorch implementation of D-LinkNet34.

    Architecture is intentionally aligned with the
    provided trained D-LinkNet34 checkpoint.
    """

    def __init__(
        self,
        num_classes: int = 1,
        pretrained_encoder: bool = False,
    ):
        super().__init__()

        # ----------------------------------------------------
        # ResNet34 encoder
        # ----------------------------------------------------

        weights = (
            ResNet34_Weights.IMAGENET1K_V1
            if pretrained_encoder
            else None
        )

        backbone = resnet34(
            weights=weights
        )

        self.firstconv = backbone.conv1
        self.firstbn = backbone.bn1
        self.firstrelu = backbone.relu
        self.firstmaxpool = backbone.maxpool

        self.encoder1 = backbone.layer1
        self.encoder2 = backbone.layer2
        self.encoder3 = backbone.layer3
        self.encoder4 = backbone.layer4

        # ----------------------------------------------------
        # D-LinkNet center
        # ----------------------------------------------------

        self.dblock = Dblock(
            512
        )

        # ----------------------------------------------------
        # Decoder
        # ----------------------------------------------------

        self.decoder4 = DecoderBlock(
            512,
            128,
            256,
        )

        self.decoder3 = DecoderBlock(
            256,
            64,
            128,
        )

        self.decoder2 = DecoderBlock(
            128,
            32,
            64,
        )

        self.decoder1 = DecoderBlock(
            64,
            16,
            64,
        )

        # ----------------------------------------------------
        # Final prediction head
        # ----------------------------------------------------

        self.finaldeconv1 = nn.ConvTranspose2d(
            64,
            32,
            kernel_size=4,
            stride=2,
            padding=1,
        )

        self.finalrelu1 = nn.ReLU(
            inplace=True
        )

        self.finalconv2 = nn.Conv2d(
            32,
            32,
            kernel_size=3,
            padding=1,
        )

        self.finalrelu2 = nn.ReLU(
            inplace=True
        )

        self.finalconv3 = nn.Conv2d(
            32,
            num_classes,
            kernel_size=3,
            padding=1,
        )

    def forward(self, x):

        # ----------------------------------------------------
        # Encoder
        # ----------------------------------------------------

        x = self.firstconv(x)
        x = self.firstbn(x)
        x = self.firstrelu(x)
        x = self.firstmaxpool(x)

        e1 = self.encoder1(x)
        e2 = self.encoder2(e1)
        e3 = self.encoder3(e2)
        e4 = self.encoder4(e3)

        # ----------------------------------------------------
        # Dilated center
        # ----------------------------------------------------

        center = self.dblock(e4)

        # ----------------------------------------------------
        # Decoder
        # ----------------------------------------------------

        d4 = self.decoder4(center)
        d4 = d4 + e3

        d3 = self.decoder3(d4)
        d3 = d3 + e2

        d2 = self.decoder2(d3)
        d2 = d2 + e1

        d1 = self.decoder1(d2)

        # ----------------------------------------------------
        # Final upsampling
        # ----------------------------------------------------

        out = self.finaldeconv1(d1)
        out = self.finalrelu1(out)

        out = self.finalconv2(out)
        out = self.finalrelu2(out)

        out = self.finalconv3(out)

        return out


# ============================================================
# ATLAS Predictor
# ============================================================

class DLinkNet34Predictor(BasePredictor):

    MODEL_NAME = "D-LinkNet34"

    ROAD_CLASS_ID = 1

    CHECKPOINT_PATH = (
        "models/dlinknet/"
        "log01_dink34.th"
    )

    def __init__(self):

        print(
            "Loading D-LinkNet34..."
        )

        self.device = torch.device(
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        print(
            f"D-LinkNet34 device: "
            f"{self.device}"
        )

        # ----------------------------------------------------
        # Model
        # ----------------------------------------------------

        self.model = DLinkNet34(
            num_classes=1,
            pretrained_encoder=False,
        )

        # ----------------------------------------------------
        # Load trained checkpoint
        # ----------------------------------------------------

        print(
            "Loading D-LinkNet34 checkpoint..."
        )

        checkpoint = torch.load(
            self.CHECKPOINT_PATH,
            map_location="cpu",
        )

        # ----------------------------------------------------
        # Checkpoint is an OrderedDict directly
        # ----------------------------------------------------

        state_dict = {
            key.replace(
                "module.",
                "",
                1,
            ): value
            for key, value in checkpoint.items()
        }

        # ----------------------------------------------------
        # Strict compatibility check
        # ----------------------------------------------------

        self.model.load_state_dict(
            state_dict,
            strict=True,
        )

        print(
            "D-LinkNet34 checkpoint "
            "loaded successfully."
        )

        self.model.to(
            self.device
        )

        self.model.eval()

        print(
            "D-LinkNet34 ready."
        )
    def predict_probabilities(
        self,
        image: Image.Image,
    ) -> np.ndarray:

        """
        Run D-LinkNet34 once and return per-pixel
        road probabilities in [0, 1].

        This is primarily used for model evaluation
        and threshold calibration.
        """

        image = image.convert("RGB")

        original_size = image.size

        # ----------------------------------------------------
        # Image -> Tensor
        # ----------------------------------------------------

        image_array = np.asarray(
            image,
            dtype=np.float32,
        ) / 255.0

        tensor = torch.from_numpy(
            image_array
        ).permute(
            2,
            0,
            1,
        )

        # ----------------------------------------------------
        # ImageNet normalization
        # ----------------------------------------------------

        mean = torch.tensor(
            [
                0.485,
                0.456,
                0.406,
            ],
            dtype=torch.float32,
        ).view(
            3,
            1,
            1,
        )

        std = torch.tensor(
            [
                0.229,
                0.224,
                0.225,
            ],
            dtype=torch.float32,
        ).view(
            3,
            1,
            1,
        )

        tensor = (
            tensor - mean
        ) / std

        tensor = tensor.unsqueeze(
            0
        ).to(
            self.device
        )

        # ----------------------------------------------------
        # Inference
        # ----------------------------------------------------

        with torch.no_grad():

            logits = self.model(
                tensor
            )

        # ----------------------------------------------------
        # Restore original dimensions
        # ----------------------------------------------------

        logits = F.interpolate(
            logits,
            size=(
                original_size[1],
                original_size[0],
            ),
            mode="bilinear",
            align_corners=False,
        )

        # ----------------------------------------------------
        # Probability
        # ----------------------------------------------------

        probabilities = torch.sigmoid(
            logits
        )[0, 0]

        return probabilities.cpu().numpy()
        
    def predict(
        self,
        image: Image.Image,
    ) -> SegmentationResult:

        start = time.perf_counter()

        # ----------------------------------------------------
        # RGB
        # ----------------------------------------------------

        image = image.convert(
            "RGB"
        )

        original_size = image.size

        # ----------------------------------------------------
        # Image → Tensor
        # ----------------------------------------------------

        image_array = np.asarray(
            image,
            dtype=np.float32,
        ) / 255.0

        tensor = torch.from_numpy(
            image_array
        ).permute(
            2,
            0,
            1,
        )

        # ----------------------------------------------------
        # ImageNet normalization
        # ----------------------------------------------------

        mean = torch.tensor(
            [
                0.485,
                0.456,
                0.406,
            ]
        ).view(
            3,
            1,
            1,
        )

        std = torch.tensor(
            [
                0.229,
                0.224,
                0.225,
            ]
        ).view(
            3,
            1,
            1,
        )

        tensor = (
            tensor - mean
        ) / std

        tensor = tensor.unsqueeze(
            0
        ).to(
            self.device
        )

        # ----------------------------------------------------
        # Inference
        # ----------------------------------------------------

        with torch.no_grad():

            logits = self.model(
                tensor
            )

        # ----------------------------------------------------
        # Restore original dimensions
        # ----------------------------------------------------

        logits = F.interpolate(
            logits,
            size=(
                original_size[1],
                original_size[0],
            ),
            mode="bilinear",
            align_corners=False,
        )

        # ----------------------------------------------------
        # Binary road mask
        # ----------------------------------------------------

        probabilities = torch.sigmoid(
            logits
        )[0, 0]

        prediction = (
            probabilities >= 0.5
        ).cpu().numpy().astype(
            np.uint8
        )

        # ----------------------------------------------------
        # Diagnostics
        # ----------------------------------------------------

        road_pixels = int(
            prediction.sum()
        )

        print(
            f"D-LinkNet road pixels: "
            f"{road_pixels}"
        )

        inference_time = (
            time.perf_counter()
            - start
        ) * 1000

        # ----------------------------------------------------
        # Result
        # ----------------------------------------------------

        return SegmentationResult(
            mask=prediction,

            model_name=self.MODEL_NAME,

            inference_time_ms=round(
                inference_time,
                2,
            ),

            image_size=original_size,

            metadata={
                "architecture": (
                    "D-LinkNet34"
                ),
                "task": (
                    "binary road extraction"
                ),
                "dataset": "DeepGlobe",
                "road_class_id": (
                    self.ROAD_CLASS_ID
                ),
                "threshold": 0.5,
                "device": str(
                    self.device
                ),
                "checkpoint": (
                    self.CHECKPOINT_PATH
                ),
            },

            # Preserve continuous road probability
            # for ensemble evaluation.
            logits=probabilities.cpu().numpy(),
        )