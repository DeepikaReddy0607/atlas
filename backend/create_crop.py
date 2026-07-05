from PIL import Image

image = Image.open("generated/hyderabad_clear.png")

print("Original size:", image.size)

crop = image.crop((0, 0, 1024, 1024))

crop.save("generated/test_crop.png")

print("Crop saved successfully!")