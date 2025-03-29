from PyQt5 import QtWidgets, uic
import rasterio
from satimgproc.edgedet import CannyEdgeDetector


class EdgedetDialog(QtWidgets.QDialog):

    def __init__(self):
        super().__init__()

        # Load UI dynamically
        uic.loadUi("ui/edgedet.ui", self)
        self.edgedetStk.setCurrentIndex(0)
        # Set up signals
        self.setupSignals()

    def setupSignals(self):
        self.inputDataBtn.clicked.connect(self.selectImage)
        self.outputDataBtn.clicked.connect(self.getOutputFolder)
        self.comboBoxEdgedet.currentTextChanged.connect(self.selectAlgorithm)
        self.generateEdgeBtn.clicked.connect(self.runEdgeDetection)

    def selectImage(self):
        """Handles file selection and sets path to the correct QLineEdit"""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Image File", "", "TIFF Files (*.tif)"
        )
        if file_path:
            self.inputDataPathTxt.setText(file_path)

    def getOutputFolder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Output Folder", ""
        )
        if folder:
            self.output_folder = folder
            self.outputDataPathTxt.setText(folder)

    def selectAlgorithm(self, text):
        self.progressBarEdgedet.setValue(0)

        if text == "Canny":
            self.edgedetStk.setCurrentWidget(self.cannyPage)
        else:
            self.edgedetStk.setCurrentIndex(0)

    def runEdgeDetection(self):
        try:
            self.progressBarEdgedet.setValue(0)

            # Step 1: Read parameters
            image_path = self.inputDataPathTxt.text()
            with rasterio.open(image_path) as src:
                image = src.read(1)  # First band for grayscale
                meta = src.meta
            output_path = self.outputDataPathTxt.text()

            # Step 2: Run edge detection
            algorithm = self.comboBoxEdgedet.currentText()

            if algorithm == "Canny":
                edge_detector = CannyEdgeDetector(
                    threshold1=self.thresh1SpinBox.value(),
                    threshold2=self.thresh2SpinBox.value(),
                )
            edge_image = edge_detector.detect(image)
            self.progressBarEdgedet.setValue(50)
            edge_detector.save_as_tif(edge_image, output_path, meta)
            self.progressBarEdgedet.setValue(100)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))
