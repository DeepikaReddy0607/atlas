from app.engines.quality.cloud import QualityAnalyzer

result = QualityAnalyzer.analyze(
    "../datasets/hyderabad/SCL_20m.jp2"
)

print(result)