from PyQt5 import QtWidgets, uic
from satimgproc.morphit import (
    ErodeOperation,
    DilateOperation,
    OpenOperation,
    CloseOperation,
)
import rasterio


class MorphitDialog(QtWidgets.QDialog):

    def __init__(self):
        super().__init__()

        # Load UI dynamically
        uic.loadUi("ui/morphit.ui", self)
        # Set up signals
        self.setupSignals()

    def setupSignals(self):
        self.inputDataBtn.clicked.connect(self.selectImage)
        self.outputDataBtn.clicked.connect(self.getOutputFolder)
        self.generateMorphBtn.clicked.connect(self.generateMorphology)

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

    def generateMorphology(self):
        self.progressBarMorph.setValue(0)

        # Step 1: Read parameters
        image_path = self.inputDataPathTxt.text()
        with rasterio.open(image_path) as src:
            image = src.read(1)  # First band for grayscale
            meta = src.meta
        # Step 2: Run edge detection
        operation_value = self.selectOperationComboBox.currentText()
        kernel_size = self.kernelSizeSpinBox.value()
        iterations = self.iterationsSpinBox.value()

        if operation_value == "Erosion":
            operation = ErodeOperation()
            morph_image = operation.apply(image, kernel_size, iterations)
        elif operation_value == "Dilation":
            operation = DilateOperation()
            morph_image = operation.apply(image, kernel_size, iterations)
        elif operation_value == "Opening":
            operation = OpenOperation()
            morph_image = operation.apply(image, kernel_size, iterations)
        elif operation_value == "Closing":
            operation = CloseOperation()
            morph_image = operation.apply(image, kernel_size, iterations)

        self.progressBarMorph.setValue(50)
        operation.save_as_tif(
            morph_image, self.outputDataPathTxt.text(), meta, operation_value
        )
        self.progressBarMorph.setValue(100)
