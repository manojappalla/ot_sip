from utils.geojson_utils import load_geometry_from_geojson
from dataset_manager import get_downloader

def main():
    """Main function to execute downloads"""
    geometry = load_geometry_from_geojson(GEOJSON_PATH)  # Load AOI from GeoJSON

    # Landsat download
    landsat_output = f"{OUTPUT_FOLDER}/landsat_pan.tif"
    landsat_downloader = get_downloader("landsat", geometry, START_DATE, END_DATE, SCALE, landsat_output)
    landsat_downloader.download()

    # Sentinel-2 download
    sentinel_output = f"{OUTPUT_FOLDER}/sentinel_rgb.tif"
    sentinel_downloader = get_downloader("sentinel", geometry, START_DATE, END_DATE, SCALE, sentinel_output)
    sentinel_downloader.download()

if __name__ == "__main__":
    main()
