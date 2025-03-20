from gee_downloader.utils.geojson_utils import load_geometry_from_geojson
from gee_downloader.dataset_manager import get_downloader

def main(dataset, geojson, start_date, end_date, cloud_cover=None):
    """Main function to initiate the download process."""
    geometry = load_geometry_from_geojson(geojson)  # Load geometry from GeoJSON

    # Get downloader instance with cloud cover filtering
    downloader = get_downloader(dataset, geometry, start_date, end_date, cloud_cover)

    # Start download
    downloader.download()
