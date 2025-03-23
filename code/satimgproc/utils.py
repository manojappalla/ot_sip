import rasterio
import json
import ee


# Used by indices.py
def load_bands(band_paths):
    """Loads raster bands from files."""
    bands = {}
    for key, path in band_paths.items():
        with rasterio.open(path) as src:
            bands[key] = [src.read(1).astype(float), src.meta.copy()]
    return bands


# Used by gee download module
def load_geometry_from_geojson(geojson_path):
    """Reads a GeoJSON file and returns an ee.Geometry"""
    with open(geojson_path, "r") as f:
        geojson = json.load(f)
    coordinates = geojson["features"][0]["geometry"]["coordinates"]
    return ee.Geometry.Polygon(coordinates)
