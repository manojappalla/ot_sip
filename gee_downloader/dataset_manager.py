from downloader.landsat_downloader import LandsatDownloader
from downloader.sentinel_downloader import SentinelDownloader

def get_downloader(dataset, geometry, start_date, end_date, scale, output_path):
    """Method to return the appropriate downloader"""
    if dataset == "landsat":
        return LandsatDownloader(geometry, start_date, end_date, scale, output_path)
    elif dataset == "sentinel":
        return SentinelDownloader(geometry, start_date, end_date, scale, output_path)
    else:
        raise ValueError("Dataset not supported! Choose 'landsat' or 'sentinel'.")
