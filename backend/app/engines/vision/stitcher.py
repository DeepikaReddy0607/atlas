import numpy as np


class MaskStitcher:

    @staticmethod
    def stitch(predictions, width, height, tile_size=512):

        final_mask = np.zeros((height, width), dtype=np.uint8)

        for mask, x, y in predictions:

            h, w = mask.shape

            final_mask[y:y+h, x:x+w] = mask

        return final_mask