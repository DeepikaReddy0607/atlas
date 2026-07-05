from enum import Enum


class VisionModel(str, Enum):

    ROAD_SEGMENTATION = "road_segmentation"

    BUILDING_SEGMENTATION = "building_segmentation"

    WATER_SEGMENTATION = "water_segmentation"

    LAND_COVER = "land_cover"