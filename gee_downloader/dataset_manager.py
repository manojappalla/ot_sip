from gee_downloader.downloader.landsat_downloader import LandsatDownloader
from gee_downloader.downloader.sentinel_downloader import SentinelDownloader


def get_downloader(dataset, geometry, start_date, end_date, cloud_cover=None):
    """Factory method to return the appropriate downloader instance with cloud cover filtering."""
    if dataset.lower() == "landsat":
        return LandsatDownloader(geometry, start_date, end_date, cloud_cover)
    elif dataset.lower() == "sentinel":
        return SentinelDownloader(geometry, start_date, end_date, cloud_cover)
    else:
        raise ValueError("Dataset not supported! Choose 'landsat' or 'sentinel'.")
