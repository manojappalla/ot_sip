import rasterio


def load_bands(band_paths):
    """Loads raster bands from files."""
    bands = {}
    for key, path in band_paths.items():
        with rasterio.open(path) as src:
            bands[key] = [src.read(1).astype(float), src.meta.copy()]
    return bands
