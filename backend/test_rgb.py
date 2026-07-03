from app.engines.geo.rgb import RGBGenerator

RGBGenerator.create_rgb(
    "../datasets/hyderabad/clear/B04.jp2",
    "../datasets/hyderabad/clear/B03.jp2",
    "../datasets/hyderabad/clear/B02.jp2",
    "generated/hyderabad_clear.png"
)

print("RGB image created successfully!")