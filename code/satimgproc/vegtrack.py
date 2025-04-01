from typing import Dict, List, Optional
import numpy as np
from datetime import datetime
import geopandas as gpd
import plotly.graph_objects as go
from sentinelhub import (
    SHConfig,
    DataCollection,
    SentinelHubCatalog,
    SentinelHubRequest,
    MimeType,
    Geometry,
    bbox_to_dimensions,
)
from satimgproc.utils import authenticateSentinelHub, load_aoi_geometry
from dask import delayed, compute


class Vegtrack:
    """
    A class for tracking vegetation (NDVI) trends over time using Sentinel Hub.

    This class fetches Sentinel-2 tiles, computes NDVI using an evalscript,
    and plots the NDVI time series for a given AOI defined in a shapefile.
    """

    def __init__(
        self,
        config: SHConfig,
        shapefile_path: str,
        start_date: str,
        end_date: str,
    ):
        """
        Initializes the Vegtrack object.

        Parameters:
        - config (SHConfig): Sentinel Hub authentication/configuration object.
        - shapefile_path (str): Path to the AOI shapefile.
        - start_date (str): Start date in 'YYYY-MM-DD' format.
        - end_date (str): End date in 'YYYY-MM-DD' format.
        """
        self.shapefile_path = shapefile_path
        self.start_date = start_date
        self.end_date = end_date
        self.cloud_coverage = 10
        self.resolution = 10
        self.config = config
        self.aoi = Geometry(load_aoi_geometry(self.shapefile_path), crs="EPSG:4326")
        self.size = bbox_to_dimensions(self.aoi.bbox, resolution=self.resolution)
        self.data_collection = DataCollection.SENTINEL2_L2A.define_from(
            "s2l2a", service_url=self.config.sh_base_url
        )
        self.evalscript = self._ndvi_evalscript()
        self.ndvi_dict = {}

    def _ndvi_evalscript(self) -> str:
        """
        Returns the JavaScript Evalscript for NDVI computation.

        Returns:
        - str: Evalscript for Sentinel Hub request.
        """
        return """
        //VERSION=3
        function setup() {
          return {
            input: ["B04", "B08", "dataMask"],
            output: { bands: 2, sampleType: "FLOAT32" }
          };
        }
        function evaluatePixel(sample) {
          let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
          return [ndvi, sample.dataMask];
        }
        """

    def fetch_tiles(self) -> List[dict]:
        """
        Searches Sentinel Hub catalog for tiles matching the AOI and time range.

        Returns:
        - list: List of tile metadata dictionaries.
        """
        catalog = SentinelHubCatalog(config=self.config)
        search_iterator = catalog.search(
            collection=self.data_collection,
            geometry=self.aoi,
            time=(self.start_date, self.end_date),
            filter=f"eo:cloud_cover < {self.cloud_coverage}",
        )
        return list(search_iterator)

    def compute_ndvi_series(self) -> None:
        """
        Computes the NDVI time series by processing all fetched tiles.

        This method populates `self.ndvi_dict` with date:mean_ndvi pairs.
        """
        tiles = self.fetch_tiles()
        tasks = []
        for tile in tiles:
            date = tile["properties"]["datetime"][:10]
            task = delayed(self._process_tile)(date)
            tasks.append(task)
        results = compute(*tasks)

    def _process_tile(self, date: str) -> None:
        """
        Processes a single tile to compute mean NDVI for a given date.

        Parameters:
        - date (str): Date in 'YYYY-MM-DD' format.
        """
        request = SentinelHubRequest(
            evalscript=self.evalscript,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=self.data_collection,
                    time_interval=(date, date),
                    mosaicking_order="leastCC",
                )
            ],
            responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
            geometry=self.aoi,
            size=self.size,
            config=self.config,
        )
        try:
            response = request.get_data()[0]
            ndvi_data = response[:, :, 0]
            mask = response[:, :, 1]
            valid_ndvi = ndvi_data[mask > 0]
            if valid_ndvi.size > 0:
                self.ndvi_dict[date] = float(np.nanmean(valid_ndvi))
        except Exception as e:
            print(f"Error processing {date}: {e}")

    def plot_ndvi(self) -> Optional[str]:
        """
        Plots the NDVI time series as an interactive Plotly graph.

        Returns:
        - str: HTML string containing the Plotly chart.
        """
        self.compute_ndvi_series()
        if not self.ndvi_dict:
            print("No NDVI data to plot. Run compute_ndvi_series() first.")
            return

        sorted_items = sorted(self.ndvi_dict.items(), key=lambda x: x[0])
        dates = [datetime.strptime(date, "%Y-%m-%d") for date, _ in sorted_items]
        ndvi_values = [float(val) for _, val in sorted_items]

        fig = go.Figure(
            data=go.Scatter(
                x=dates,
                y=ndvi_values,
                mode="lines+markers",
                marker=dict(color="green"),
                line=dict(width=2),
                hovertemplate="Date: %{x|%Y-%m-%d}<br>NDVI: %{y:.3f}<extra></extra>",
            )
        )

        fig.update_layout(
            title="NDVI Time Series over AOI",
            xaxis_title="Date",
            yaxis_title="Mean NDVI",
            hovermode="x unified",
            template="plotly_white",
        )

        html = fig.to_html(include_plotlyjs="cdn")
        return html
