import rasterio
import numpy as np
from PIL import Image


class RGBGenerator:

    @staticmethod
    def create_rgb(red_path, green_path, blue_path, output_path):

        with rasterio.open(red_path) as r:
            red = r.read(1)

        with rasterio.open(green_path) as g:
            green = g.read(1)

        with rasterio.open(blue_path) as b:
            blue = b.read(1)

        rgb = np.dstack((red, green, blue))

        rgb = rgb.astype(np.float32)

        rgb = (rgb - rgb.min()) / (rgb.max() - rgb.min())

        rgb = (rgb * 255).astype(np.uint8)

        image = Image.fromarray(rgb)

        image.save(output_path)