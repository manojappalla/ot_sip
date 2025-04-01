from typing import Dict, Any
import rasterio
import json
import ee
import geopandas as gpd
from sentinelhub import SHConfig


# Used by phenotrack and SentinelHub download
def authenticateSentinelHub(args: Dict[str, str]) -> SHConfig:
    """
    Authenticates with the Copernicus Data Space Ecosystem (Sentinel Hub).

    Parameters:
    - args (dict): Dictionary containing:
        - "sh_client_id" (str): Sentinel Hub client ID.
        - "sh_client_secret" (str): Sentinel Hub client secret.

    Returns:
    - SHConfig: Configured Sentinel Hub authentication object.
    """
    config = SHConfig()
    config.sh_client_id = args["sh_client_id"]
    config.sh_client_secret = args["sh_client_secret"]
    config.sh_token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
    config.sh_base_url = "https://sh.dataspace.copernicus.eu"
    return config


# Used by indices.py
def load_bands(band_paths: Dict[str, str]) -> Dict[str, Any]:
    """
    Loads multiple raster bands from disk for index computation.

    Parameters:
    - band_paths (dict): Dictionary mapping band names to file paths.

    Returns:
    - dict: Mapping of band names to [array, metadata] lists.
    """
    bands = {}
    for key, path in band_paths.items():
        with rasterio.open(path) as src:
            bands[key] = [src.read(1).astype(float), src.meta.copy()]
    return bands


# Used by gee download module
def load_geometry_from_geojson(geojson_path: str) -> ee.Geometry:
    """
    Loads a geometry from a GeoJSON file for Earth Engine operations.

    Parameters:
    - geojson_path (str): Path to the GeoJSON file.

    Returns:
    - ee.Geometry.Polygon: Earth Engine polygon geometry.
    """
    with open(geojson_path, "r") as f:
        geojson = json.load(f)
    coordinates = geojson["features"][0]["geometry"]["coordinates"]
    return ee.Geometry.Polygon(coordinates)


# Used by phenotrack.py
def load_aoi_geometry(shp_path: str) -> Dict:
    """
    Loads an area of interest (AOI) geometry from a shapefile and converts it to GeoJSON.

    Parameters:
    - shp_path (str): Path to the shapefile.

    Returns:
    - dict: GeoJSON-style geometry dictionary (__geo_interface__).
    """
    gdf = gpd.read_file(shp_path)
    gdf = gdf.to_crs("EPSG:4326")
    aoi_geometry = gdf.geometry.iloc[0].__geo_interface__
    return aoi_geometry
