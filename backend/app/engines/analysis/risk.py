class RiskAssessment:

    @staticmethod
    def classify(ari: float):

        if ari >= 0.80:
            return "LOW"

        elif ari >= 0.60:
            return "MODERATE"

        elif ari >= 0.40:
            return "ELEVATED"

        elif ari >= 0.20:
            return "HIGH"

        return "CRITICAL"

    @staticmethod
    def recommendation(level: str):

        recommendations = {
            "LOW":
                "Network is resilient. Routine monitoring recommended.",

            "MODERATE":
                "Monitor critical junctions and maintain redundancy.",

            "ELEVATED":
                "Strengthen vulnerable road segments and prepare contingency routes.",

            "HIGH":
                "Immediate redundancy planning recommended. Failure may isolate regions.",

            "CRITICAL":
                "Immediate intervention required. Network is highly vulnerable.",
        }

        return recommendations[level]