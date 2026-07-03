import rasterio


class GeoReader:

    @staticmethod
    def read_metadata(file_path):

        with rasterio.open(file_path) as src:

            return {
                "driver": src.driver,
                "width": src.width,
                "height": src.height,
                "bands": src.count,
                "crs": str(src.crs),
                "bounds": {
                    "left": src.bounds.left,
                    "bottom": src.bounds.bottom,
                    "right": src.bounds.right,
                    "top": src.bounds.top,
                },
                "resolution": {
                    "x": src.res[0],
                    "y": src.res[1],
                },
                "dtype": src.dtypes[0],
            }