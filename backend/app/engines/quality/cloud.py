import rasterio
import numpy as np


class QualityAnalyzer:

    # Sentinel-2 Scene Classification values
    CLOUD_CLASSES = [8, 9, 10]
    SHADOW_CLASS = 3
    WATER_CLASS = 6
    VEGETATION_CLASS = 4

    @staticmethod
    def analyze(scl_path):

        with rasterio.open(scl_path) as src:
            scl = src.read(1)

        total_pixels = scl.size

        def percentage(mask):
            return round(mask.sum() / total_pixels * 100, 2)

        cloud_mask = np.isin(scl, QualityAnalyzer.CLOUD_CLASSES)

        shadow_mask = scl == QualityAnalyzer.SHADOW_CLASS

        water_mask = scl == QualityAnalyzer.WATER_CLASS

        vegetation_mask = scl == QualityAnalyzer.VEGETATION_CLASS

        cloud_percentage = percentage(cloud_mask)

        if cloud_percentage < 10:
            quality = "EXCELLENT"
        elif cloud_percentage < 25:
            quality = "GOOD"
        elif cloud_percentage < 50:
            quality = "FAIR"
        else:
            quality = "POOR"

        return {
            "cloud_percentage": cloud_percentage,
            "shadow_percentage": percentage(shadow_mask),
            "water_percentage": percentage(water_mask),
            "vegetation_percentage": percentage(vegetation_mask),
            "quality": quality,
            "recommended_for_analysis": cloud_percentage < 50,
            "decision": (
                "Proceed with analysis"
                if cloud_percentage < 50
                else "Reject image and acquire another Sentinel-2 scene"
            )
        }