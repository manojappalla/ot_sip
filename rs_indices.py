from PyQt5 import QtWidgets, uic
from indices_app.indices.vegetation import VegetationIndices
from indices_app.indices.water import WaterIndices
from indices_app.indices.geology import GeologyIndices
from indices_app.indices.land import LandIndices


class IndicesWindow(QtWidgets.QDialog):

    def __init__(self):
        super().__init__()

        # Load UI dynamically
        uic.loadUi("ui/indices.ui", self)

        # Set up signals
        self.setupSignals()

        # Initialize authentication thread
        self.auth_thread = None

    def setupSignals(self):
        """Connect UI elements to their functions."""
        self.band_button_map = {
            self.blueBandPathBtnVI: self.blueBandPathVI,
            self.greenBandPathBtnVI: self.greenBandPathVI,
            self.redBandPathBtnVI: self.redBandPathVI,
            self.nirBandPathBtnVI: self.nirBandPathVI,
            self.greenBandPathBtnWI: self.greenBandPathWI,
            self.nirBandPathBtnWI: self.nirBandPathWI,
            self.swir1BandPathBtnWI: self.swir1BandPathWI,
            self.swir2BandPathBtnWI: self.swir2BandPathWI,
            self.blueBandPathBtnGI: self.blueBandPathGI,
            self.redBandPathBtnGI: self.redBandPathGI,
            self.nirBandPathBtnGI: self.nirBandPathGI,
            self.swir1BandPathBtnGI: self.swir1BandPathGI,
            self.swir2BandPathBtnGI: self.swir2BandPathGI,
            self.redBandPathBtnLI: self.redBandPathLI,
            self.nirBandPathBtnLI: self.nirBandPathLI,
            self.swir1BandPathBtnLI: self.swir1BandPathLI,
        }
        self.blueBandPathBtnVI.clicked.connect(self.selectBand)
        self.greenBandPathBtnVI.clicked.connect(self.selectBand)
        self.redBandPathBtnVI.clicked.connect(self.selectBand)
        self.nirBandPathBtnVI.clicked.connect(self.selectBand)

        self.greenBandPathBtnWI.clicked.connect(self.selectBand)
        self.nirBandPathBtnWI.clicked.connect(self.selectBand)
        self.swir1BandPathBtnWI.clicked.connect(self.selectBand)
        self.swir2BandPathBtnWI.clicked.connect(self.selectBand)

        self.blueBandPathBtnGI.clicked.connect(self.selectBand)
        self.redBandPathBtnGI.clicked.connect(self.selectBand)
        self.nirBandPathBtnGI.clicked.connect(self.selectBand)
        self.swir1BandPathBtnGI.clicked.connect(self.selectBand)
        self.swir2BandPathBtnGI.clicked.connect(self.selectBand)

        self.redBandPathBtnLI.clicked.connect(self.selectBand)
        self.nirBandPathBtnLI.clicked.connect(self.selectBand)
        self.swir1BandPathBtnLI.clicked.connect(self.selectBand)

        self.outputPathBtnVI.clicked.connect(self.selectOutputFolder)
        self.outputPathBtnWI.clicked.connect(self.selectOutputFolder)
        self.outputPathBtnGI.clicked.connect(self.selectOutputFolder)
        self.outputPathBtnLI.clicked.connect(self.selectOutputFolder)

        self.generateBtnVI.clicked.connect(self.generateIndices)
        self.generateBtnWI.clicked.connect(self.generateIndices)
        self.generateBtnGI.clicked.connect(self.generateIndices)
        self.generateBtnLI.clicked.connect(self.generateIndices)

    def selectBand(self):
        """Handles file selection and sets path to the correct QLineEdit"""
        button = self.sender()  # The button that triggered the signal
        line_edit = self.band_button_map.get(button)

        if line_edit:
            file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, "Select Band File", "", "TIFF Files (*.tif)"
            )
            if file_path:
                line_edit.setText(file_path)

    def setBlueBandPathVI(self):
        fileName = self.selectBand()

    def selectOutputFolder(self):
        """Open a file dialog to select an output folder."""
        current_index = self.indicesTab.currentIndex()
        options = QtWidgets.QFileDialog.Options()
        folderName = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            "",
            options=options,
        )
        if folderName and current_index == 0:
            self.outputPathVI.setText(folderName)
        elif folderName and current_index == 1:
            self.outputPathWI.setText(folderName)
        elif folderName and current_index == 2:
            self.outputPathGI.setText(folderName)
        elif folderName and current_index == 3:
            self.outputPathLI.setText(folderName)

    def generateIndices(self):
        if self.ndviRBtn.isChecked():
            red_band_path = self.redBandPathVI.text()
            nir_band_path = self.nirBandPathVI.text()
            band_paths = {"red": red_band_path, "nir": nir_band_path}
            vegetation_indices = VegetationIndices(band_paths, self.outputPathVI.text())
            vegetation_indices.ndvi()
            self.ndviRBtn.setAutoExclusive(False)
            self.ndviRBtn.setChecked(False)

        elif self.msaviRBtn.isChecked():
            red_band_path = self.redBandPathVI.text()
            nir_band_path = self.nirBandPathVI.text()
            band_paths = {"red": red_band_path, "nir": nir_band_path}
            vegetation_indices = VegetationIndices(band_paths, self.outputPathVI.text())
            vegetation_indices.msavi()
            self.msaviRBtn.setAutoExclusive(False)
            self.msaviRBtn.setChecked(False)

        elif self.variRBtn.isChecked():
            blue_band_path = self.blueBandPathVI.text()
            green_band_path = self.greenBandPathVI.text()
            red_band_path = self.redBandPathVI.text()
            band_paths = {
                "blue": blue_band_path,
                "green": green_band_path,
                "red": red_band_path,
            }
            vegetation_indices = VegetationIndices(band_paths, self.outputPathVI.text())
            vegetation_indices.vari()
            self.variRBtn.setAutoExclusive(False)
            self.variRBtn.setChecked(False)

        elif self.mndwiRBtn.isChecked():
            green_band_path = self.greenBandPathWI.text()
            swir1_band_path = self.swir1BandPathWI.text()
            band_paths = {"green": green_band_path, "swir1": swir1_band_path}
            water_indices = WaterIndices(band_paths, self.outputPathWI.text())
            water_indices.mndwi()
            self.mndwiRBtn.setAutoExclusive(False)
            self.mndwiRBtn.setChecked(False)

        elif self.ndmiRBtn.isChecked():
            nir_band_path = self.nirBandPathWI.text()
            swir1_band_path = self.swir1BandPathWI.text()
            band_paths = {"nir": nir_band_path, "swir1": swir1_band_path}
            water_indices = WaterIndices(band_paths, self.outputPathWI.text())
            water_indices.ndmi()
            self.ndmiRBtn.setAutoExclusive(False)
            self.ndmiRBtn.setChecked(False)

        elif self.clayRBtn.isChecked():
            swir1_band_path = self.swir1BandPathGI.text()
            swir2_band_path = self.swir2BandPathGI.text()
            band_paths = {"swir1": swir1_band_path, "swir2": swir2_band_path}
            geology_indices = GeologyIndices(band_paths, self.outputPathGI.text())
            geology_indices.clay()
            self.clayRBtn.setAutoExclusive(False)
            self.clayRBtn.setChecked(False)

        elif self.ferrousRBtn.isChecked():
            nir_band_path = self.nirBandPathGI.text()
            swir1_band_path = self.swir1BandPathGI.text()
            band_paths = {"nir": nir_band_path, "swir1": swir1_band_path}
            geology_indices = GeologyIndices(band_paths, self.outputPathGI.text())
            geology_indices.ferrous()
            self.ferrousRBtn.setAutoExclusive(False)
            self.ferrousRBtn.setChecked(False)

        elif self.ioRBtn.isChecked():
            blue_band_path = self.blueBandPathGI.text()
            red_band_path = self.redBandPathGI.text()
            band_paths = {"blue": blue_band_path, "red": red_band_path}
            geology_indices = GeologyIndices(band_paths, self.outputPathGI.text())
            geology_indices.iron_oxide()
            self.ioRBtn.setAutoExclusive(False)
            self.ioRBtn.setChecked(False)

        elif self.baiRBtn.isChecked():
            red_band_path = self.redBandPathLI.text()
            nir_band_path = self.nirBandPathLI.text()
            band_paths = {"red": red_band_path, "nir": nir_band_path}
            land_indices = LandIndices(band_paths, self.outputPathLI.text())
            land_indices.bai()
            self.baiRBtn.setAutoExclusive(False) 
            self.baiRBtn.setChecked(False)

        elif self.nbrRBtn.isChecked():
            nir_band_path = self.nirBandPathLI.text()
            swir1_band_path = self.swir1BandPathLI.text()
            band_paths = {"nir": nir_band_path, "swir1": swir1_band_path}
            land_indices = LandIndices(band_paths, self.outputPathLI.text())
            land_indices.nbr()
            self.nbrRBtn.setAutoExclusive(False) 
            self.nbrRBtn.setChecked(False)

        elif self.ndbiRBtn.isChecked():
            nir_band_path = self.nirBandPathLI.text()
            swir1_band_path = self.swir1BandPathLI.text()
            band_paths = {"nir": nir_band_path, "swir1": swir1_band_path}
            land_indices = LandIndices(band_paths, self.outputPathLI.text())
            land_indices.ndbi()
            self.ndbiRBtn.setAutoExclusive(False) 
            self.ndbiRBtn.setChecked(False)
