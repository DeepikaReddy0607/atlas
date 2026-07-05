from PIL import Image


class ImageTiler:

    @staticmethod
    def split(image, tile_size=512):

        tiles = []

        width, height = image.size

        for y in range(0, height, tile_size):
            for x in range(0, width, tile_size):

                tile = image.crop(
                    (
                        x,
                        y,
                        min(x + tile_size, width),
                        min(y + tile_size, height),
                    )
                )

                tiles.append((tile, x, y))

        return tiles