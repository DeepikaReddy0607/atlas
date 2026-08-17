import numpy as np


class MaskStitcher:

    @staticmethod
    def stitch_logits(
        predictions,
        width,
        height,
        num_classes,
    ):

        logits_sum = np.zeros(
            (
                num_classes,
                height,
                width,
            ),
            dtype=np.float32,
        )

        counts = np.zeros(
            (
                height,
                width,
            ),
            dtype=np.float32,
        )

        for logits, x, y in predictions:

            h = logits.shape[1]
            w = logits.shape[2]

            logits_sum[
                :,
                y:y + h,
                x:x + w,
            ] += logits

            counts[
                y:y + h,
                x:x + w,
            ] += 1.0

        counts[
            counts == 0
        ] = 1.0

        averaged_logits = (
            logits_sum
            / counts[None, :, :]
        )

        return averaged_logits

    @staticmethod
    def stitch(
        predictions,
        width,
        height,
        tile_size=512,
    ):

        final_mask = np.zeros(
            (
                height,
                width,
            ),
            dtype=np.uint8,
        )

        for mask, x, y in predictions:

            h, w = mask.shape

            final_mask[
                y:y + h,
                x:x + w,
            ] = mask

        return final_mask