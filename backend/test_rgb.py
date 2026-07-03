from app.engines.geo.rgb import RGBGenerator

RGBGenerator.create_rgb(
    "../datasets/hyderabad/B04.jp2",
    "../datasets/hyderabad/B03.jp2",
    "../datasets/hyderabad/B02.jp2",
    "generated/hyderabad_rgb.png"
)

print("RGB image created successfully!")