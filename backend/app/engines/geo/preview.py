import rasterio
from rasterio.plot import reshape_as_image
import matplotlib.pyplot as plt


class GeoPreview:

    @staticmethod
    def generate_preview(input_path, output_path):

        with rasterio.open(input_path) as src:

            image = src.read([1, 2, 3])

            image = reshape_as_image(image)

            plt.figure(figsize=(8, 8))
            plt.imshow(image)
            plt.axis("off")
            plt.savefig(output_path, bbox_inches="tight")
            plt.close()