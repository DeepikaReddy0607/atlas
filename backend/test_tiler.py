from PIL import Image

from app.engines.vision.tiler import ImageTiler

image = Image.open(
    "generated/hyderabad_clear.png"
)

tiles = ImageTiler.split(image)

print(f"Tiles: {len(tiles)}")

tile, x, y = tiles[0]

tile.save("generated/tile0.png")