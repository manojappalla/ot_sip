import rasterio
import json
import ee
import geopandas as gpd
from sentinelhub import SHConfig


# Used by phenotrack and SentinelHub download
def authenticateSentinelHub(args):
    config = SHConfig()
    config.sh_client_id = args["sh_client_id"]
    config.sh_client_secret = args["sh_client_secret"]
    config.sh_token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
    config.sh_base_url = "https://sh.dataspace.copernicus.eu"
    return config


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


# Used by phenotrack.py
def load_aoi_geometry(shp_path):
    """Loads the area of interest (AOI) geometry from a shapefile."""
    gdf = gpd.read_file(shp_path)
    gdf = gdf.to_crs("EPSG:4326")
    aoi_geometry = gdf.geometry.iloc[0].__geo_interface__
    return aoi_geometry
