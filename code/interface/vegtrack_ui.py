import requests
from PyQt5 import QtWidgets, uic
from satimgproc.vegtrack import Vegtrack
from satimgproc.utils import authenticateSentinelHub


class VegtrackDialog(QtWidgets.QDialog):

    def __init__(self):
        super().__init__()

        # Load UI dynamically
        uic.loadUi("ui/vegtrack.ui", self)
        self.config = None
        # Set up signals
        self.setupSignals()

    def setupSignals(self):
        self.sentinelhubAuthBtn.clicked.connect(self.authenticate)
        self.inputShpPathBtn.clicked.connect(self.selectShapefile)
        self.generateVegCurveBtn.clicked.connect(self.generateVegcurve)

    def authenticate(self):
        config_args = {
            "sh_client_id": self.clientIdTxt.text(),
            "sh_client_secret": self.clientSecretTxt.text(),
        }
        config = authenticateSentinelHub(config_args)
        payload = {
            "grant_type": "client_credentials",
            "client_id": config.sh_client_id,
            "client_secret": config.sh_client_secret,
        }
        token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
        response = requests.post(token_url, data=payload)
        if response.status_code == 200:
            self.loginStatusLbl.setText("Login Successful")
            self.loginStatusLbl.setStyleSheet("color: green;")
            self.config = config
        else:
            self.loginStatusLbl.setText("Login Failed")
            self.loginStatusLbl.setStyleSheet("color: red;")
            self.config = None

    def selectShapefile(self):
        """Open a file dialog to select a GeoJSON file."""
        options = QtWidgets.QFileDialog.Options()
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select Shapefile",
            "",
            "Shapefiles (*.shp)",
            options=options,
        )
        if fileName:
            self.inputShpPathTxt.setText(
                fileName
            )  # Update the text box with the selected file path

    def generateVegcurve(self):
        vegtrack = Vegtrack(
            self.config,
            self.inputShpPathTxt.text(),
            self.startDateSelectVeg.date().toString("yyyy-MM-dd"),
            self.endDateSelectVeg.date().toString("yyyy-MM-dd"),
        )
        html = vegtrack.plot_ndvi()
        self.webViewVeg.setHtml(html)
