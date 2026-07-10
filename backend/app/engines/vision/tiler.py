from dataclasses import dataclass
from PIL import Image


@dataclass
class Tile:

    image: Image.Image

    x: int

    y: int

    index: int


class ImageTiler:

    @staticmethod
    def split(
        image: Image.Image,
        tile_size: int = 512,
    ):

        tiles = []

        width, height = image.size

        index = 0

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

                tiles.append(
                    Tile(
                        image=tile,
                        x=x,
                        y=y,
                        index=index,
                    )
                )

                index += 1

        return tiles