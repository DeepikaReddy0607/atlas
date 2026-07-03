from app.engines.quality.cloud import QualityAnalyzer

result = QualityAnalyzer.analyze(
    "generated/hyderabad_rgb.png"
)

print(result)