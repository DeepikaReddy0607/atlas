from pathlib import Path
import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image

from app.engines.vision.result import SegmentationResult


# ============================================================
# RoadGIE Decoder Block
# ============================================================

class DecoderBlock(nn.Module):

    def __init__(
        self,
        in_channels,
        n_filters,
        BatchNorm,
        inp=False,
    ):
        super().__init__()

        self.conv1 = nn.Conv2d(
            in_channels,
            in_channels // 4,
            1,
        )

        self.bn1 = BatchNorm(
            in_channels // 4
        )

        self.relu1 = nn.ReLU()

        self.inp = inp

        self.deconv1 = nn.Conv2d(
            in_channels // 4,
            in_channels // 4,
            (1, 9),
            padding=(0, 4),
        )

        self.deconv2 = nn.Conv2d(
            in_channels // 4,
            in_channels // 4,
            (9, 1),
            padding=(4, 0),
        )

        self.deconv3 = nn.Conv2d(
            in_channels // 4,
            in_channels // 4,
            (9, 1),
            padding=(4, 0),
        )

        self.deconv4 = nn.Conv2d(
            in_channels // 4,
            in_channels // 4,
            (1, 9),
            padding=(0, 4),
        )

        self.bn2 = BatchNorm(
            in_channels
        )

        self.relu2 = nn.ReLU()

        self.conv3 = nn.Conv2d(
            in_channels,
            n_filters,
            1,
        )

        self.bn3 = BatchNorm(
            n_filters
        )

        self.relu3 = nn.ReLU()

        self._init_weight()

    def forward(
        self,
        x,
        inp=False,
    ):

        x = x.to(
            dtype=torch.float32
        )

        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu1(x)

        x1 = self.deconv1(x)
        x2 = self.deconv2(x)

        x3 = self.inv_h_transform(
            self.deconv3(
                self.h_transform(x)
            )
        )

        x4 = self.inv_v_transform(
            self.deconv4(
                self.v_transform(x)
            )
        )

        x = torch.cat(
            (
                x1,
                x2,
                x3,
                x4,
            ),
            dim=1,
        )

        if self.inp:

            x = F.interpolate(
                x,
                scale_factor=2,
                mode="bilinear",
                align_corners=False,
            )

        x = self.bn2(x)
        x = self.relu2(x)

        x = self.conv3(x)
        x = self.bn3(x)
        x = self.relu3(x)

        return x

    def _init_weight(self):

        for module in self.modules():

            if isinstance(
                module,
                nn.Conv2d,
            ):
                nn.init.kaiming_normal_(
                    module.weight
                )

            elif isinstance(
                module,
                nn.BatchNorm2d,
            ):
                module.weight.data.fill_(
                    1
                )

                module.bias.data.zero_()

    def h_transform(self, x):

        shape = x.size()

        x = F.pad(
            x,
            (0, shape[-1]),
        )

        x = x.reshape(
            shape[0],
            shape[1],
            -1,
        )[..., :-shape[-1]]

        x = x.reshape(
            shape[0],
            shape[1],
            shape[2],
            2 * shape[3] - 1,
        )

        return x

    def inv_h_transform(self, x):

        shape = x.size()

        x = x.reshape(
            shape[0],
            shape[1],
            -1,
        ).contiguous()

        x = F.pad(
            x,
            (0, shape[-2]),
        )

        x = x.reshape(
            shape[0],
            shape[1],
            shape[-2],
            2 * shape[-2],
        )

        x = x[
            ...,
            0:shape[-2],
        ]

        return x

    def v_transform(self, x):

        x = x.permute(
            0,
            1,
            3,
            2,
        )

        shape = x.size()

        x = F.pad(
            x,
            (0, shape[-1]),
        )

        x = x.reshape(
            shape[0],
            shape[1],
            -1,
        )[..., :-shape[-1]]

        x = x.reshape(
            shape[0],
            shape[1],
            shape[2],
            2 * shape[3] - 1,
        )

        return x.permute(
            0,
            1,
            3,
            2,
        )

    def inv_v_transform(self, x):

        x = x.permute(
            0,
            1,
            3,
            2,
        )

        shape = x.size()

        x = x.reshape(
            shape[0],
            shape[1],
            -1,
        )

        x = F.pad(
            x,
            (0, shape[-2]),
        )

        x = x.reshape(
            shape[0],
            shape[1],
            shape[-2],
            2 * shape[-2],
        )

        x = x[
            ...,
            0:shape[-2],
        ]

        return x.permute(
            0,
            1,
            3,
            2,
        )


# ============================================================
# Decoder wrapper
# ============================================================

class DecoderConvWrapper(nn.Module):

    def __init__(
        self,
        in_channels,
        out_channels,
        kernel_size,
        padding,
        do_activation=True,
    ):
        super().__init__()

        self.block = DecoderBlock(
            in_channels,
            out_channels,
            BatchNorm=nn.BatchNorm2d,
            inp=False,
        )

    def forward(self, x):

        return self.block(x)


# ============================================================
# Normal RoadGIE convolution
# ============================================================

class Conv2d(nn.Module):

    def __init__(
        self,
        in_channels,
        out_channels,
        kernel_size,
        padding,
        do_activation=True,
    ):
        super().__init__()

        layers = [
            nn.Conv2d(
                in_channels,
                out_channels,
                kernel_size=kernel_size,
                padding=padding,
            )
        ]

        if do_activation:

            layers.append(
                nn.PReLU()
            )

        self.conv = nn.Sequential(
            *layers
        )

    def forward(self, x):

        return self.conv(x)


# ============================================================
# RoadGIE U-Net
# ============================================================

class _UNet(nn.Module):

    def __init__(
        self,
        in_channels=1,
        out_channels=1,
        features=None,
        conv_kernel_size=3,
        conv=None,
        conv_kwargs=None,
    ):
        super().__init__()

        if features is None:

            features = [
                64,
                64,
                64,
                64,
                64,
            ]

        if conv_kwargs is None:
            conv_kwargs = {}

        self.in_channels = in_channels

        padding = (
            conv_kernel_size - 1
        ) // 2

        self.ups = nn.ModuleList()

        self.downs = nn.ModuleList()

        self.pool = nn.MaxPool2d(
            kernel_size=2,
            stride=2,
        )

        # ----------------------------------------------------
        # Encoder
        # ----------------------------------------------------

        for i, feat in enumerate(
            features
        ):

            self.downs.append(
                conv(
                    in_channels,
                    feat,
                    kernel_size=conv_kernel_size,
                    padding=padding,
                    **conv_kwargs,
                )
            )

            in_channels = feat

        # ----------------------------------------------------
        # Decoder
        # ----------------------------------------------------

        for i, feat in enumerate(
            reversed(features)
        ):

            self.ups.append(
                nn.UpsamplingBilinear2d(
                    scale_factor=2
                )
            )

            if i in [3]:

                self.ups.append(
                    DecoderConvWrapper(
                        feat * 2,
                        feat,
                        kernel_size=conv_kernel_size,
                        padding=padding,
                        **conv_kwargs,
                    )
                )

            else:

                self.ups.append(
                    conv(
                        feat * 2,
                        feat,
                        kernel_size=conv_kernel_size,
                        padding=padding,
                        **conv_kwargs,
                    )
                )

        # ----------------------------------------------------
        # Bottleneck
        # ----------------------------------------------------

        self.bottleneck = conv(
            features[-1],
            features[-1],
            kernel_size=conv_kernel_size,
            padding=padding,
            **conv_kwargs,
        )

        # ----------------------------------------------------
        # Final convolution
        # ----------------------------------------------------

        self.final_conv = conv(
            features[0],
            out_channels,
            kernel_size=1,
            padding=0,
            do_activation=False,
            **conv_kwargs,
        )

        self.gradcam_activation = None

    def forward(self, x):

        skip_connections = []

        for down in self.downs:

            x = down(x)

            skip_connections.append(
                x
            )

            x = self.pool(x)

        x = self.bottleneck(x)

        skip_connections = (
            skip_connections[::-1]
        )

        for idx in range(
            0,
            len(self.ups),
            2,
        ):

            x = self.ups[idx](x)

            skip_connection = (
                skip_connections[
                    idx // 2
                ]
            )

            x = torch.cat(
                (
                    skip_connection,
                    x,
                ),
                dim=1,
            )

            x = self.ups[
                idx + 1
            ](x)

        return self.final_conv(x)


class UNet(_UNet):

    def __init__(
        self,
        **kwargs,
    ):

        super().__init__(
            conv=Conv2d,
            **kwargs,
        )


# ============================================================
# RoadGIE Predictor
# ============================================================

class RoadGIEPredictor:

    CHECKPOINT_PATH = (
        Path(__file__).resolve().parents[5]
        / "RoadGIE"
        / "checkpoint"
        / "epoch-last.pt"
    )

    INPUT_SIZE = (
        512,
        512,
    )

    THRESHOLD = 0.50

    def __init__(self):

        print(
            "Loading RoadGIE..."
        )

        self.device = torch.device(
            "cpu"
        )

        print(
            f"RoadGIE device: {self.device}"
        )

        if not self.CHECKPOINT_PATH.exists():

            raise FileNotFoundError(
                "RoadGIE checkpoint not found: "
                f"{self.CHECKPOINT_PATH}"
            )

        self.model = UNet(
            in_channels=6,
            out_channels=1,
            features=[
                192,
                192,
                192,
                192,
            ],
        )

        print(
            "Loading RoadGIE checkpoint..."
        )

        checkpoint = torch.load(
            self.CHECKPOINT_PATH,
            map_location=self.device,
            weights_only=False,
        )

        if "model" not in checkpoint:

            raise ValueError(
                "RoadGIE checkpoint does not "
                "contain a 'model' state dictionary."
            )

        state_dict = checkpoint[
            "model"
        ]

        cleaned_state_dict = {}

        for key, value in state_dict.items():

            if key.startswith(
                "module."
            ):

                key = key[
                    len("module.") :
                ]

            cleaned_state_dict[
                key
            ] = value

        self.model.load_state_dict(
            cleaned_state_dict,
            strict=True,
        )

        self.model = self.model.to(
            self.device
        )

        self.model.eval()

        total_parameters = sum(
            parameter.numel()
            for parameter in self.model.parameters()
        )

        print(
            "RoadGIE parameters: "
            f"{total_parameters / 1e6:.2f}M"
        )

        print(
            "RoadGIE checkpoint "
            "loaded successfully."
        )

        print(
            "RoadGIE ready."
        )

    # ========================================================
    # Input preparation
    # ========================================================

    def _prepare_image(
        self,
        image: Image.Image,
    ):

        image = image.convert(
            "RGB"
        )

        original_width, original_height = (
            image.size
        )

        image_array = np.asarray(
            image,
            dtype=np.float32,
        )

        image_array /= 255.0

        tensor = torch.from_numpy(
            image_array
        )

        tensor = tensor.permute(
            2,
            0,
            1,
        )

        tensor = tensor.unsqueeze(
            0
        )

        tensor = F.interpolate(
            tensor,
            size=self.INPUT_SIZE,
            mode="bilinear",
            align_corners=False,
        )

        # RoadGIE network expects six channels.
        #
        # The first three are the RGB image.
        # The remaining three channels are initialized
        # to zero for automatic road extraction.

        auxiliary = torch.zeros(
            (
                1,
                3,
                self.INPUT_SIZE[0],
                self.INPUT_SIZE[1],
            ),
            dtype=tensor.dtype,
        )

        tensor = torch.cat(
            (
                tensor,
                auxiliary,
            ),
            dim=1,
        )

        return (
            tensor.to(self.device),
            (
                original_width,
                original_height,
            ),
        )

    # ========================================================
    # Probability prediction
    # ========================================================

    def predict_probabilities(
        self,
        image: Image.Image,
    ):

        input_tensor, original_size = (
            self._prepare_image(
                image
            )
        )

        start = time.perf_counter()

        with torch.no_grad():

            logits = self.model(
                input_tensor
            )

            probabilities = torch.sigmoid(
                logits
            )

        inference_time_ms = (
            time.perf_counter() - start
        ) * 1000.0

        probabilities = F.interpolate(
            probabilities,
            size=(
                original_size[1],
                original_size[0],
            ),
            mode="bilinear",
            align_corners=False,
        )

        probability_map = (
            probabilities[
                0,
                0,
            ]
            .cpu()
            .numpy()
        )

        return (
            probability_map,
            inference_time_ms,
        )

    # ========================================================
    # ATLAS predictor interface
    # ========================================================

    def predict(
        self,
        image: Image.Image,
    ) -> SegmentationResult:

        probability_map, inference_time_ms = (
            self.predict_probabilities(
                image
            )
        )

        mask = (
            probability_map
            >= self.THRESHOLD
        ).astype(
            np.uint8
        )

        return SegmentationResult(
        mask=mask,
        model_name="RoadGIE",
        inference_time_ms=inference_time_ms,
        image_size=image.size,
        metadata={
            "output_type": "binary_road",
            "threshold": self.THRESHOLD,
            "road_class_id": None,
            "probability_min": float(
                probability_map.min()
            ),
            "probability_max": float(
                probability_map.max()
            ),
            "probability_mean": float(
                probability_map.mean()
            ),
        },
        logits=probability_map,
    )