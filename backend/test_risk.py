from app.engines.analysis.risk import RiskAssessment

ari = 0.30

level = RiskAssessment.classify(ari)

print("ARI:", ari)
print("Risk:", level)
print("Recommendation:")
print(RiskAssessment.recommendation(level))