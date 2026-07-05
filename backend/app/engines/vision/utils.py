from PIL import Image


class VisionUtils:

    @staticmethod
    def save(image, output_path):

        image.save(output_path)