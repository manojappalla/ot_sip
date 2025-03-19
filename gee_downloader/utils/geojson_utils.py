import json
import ee

def load_geometry_from_geojson(geojson_path):
    """Reads a GeoJSON file and returns an ee.Geometry"""
    with open(geojson_path, "r") as f:
        geojson = json.load(f)
    coordinates = geojson["features"][0]["geometry"]["coordinates"]
    return ee.Geometry.Polygon(coordinates)
