from PyQt5 import QtWidgets, uic
from satimgproc.classify import DataPreprocessor, KMeans as CustomKMeans
import rasterio
import geopandas as gpd
import os
import sys
import numpy as np


class UnsupervisedDialog(QtWidgets.QDialog):

    def __init__(self):
        super().__init__()

        # Load UI dynamically
        uic.loadUi("ui/unsupervised.ui", self)

        # Set up signals
        self.setupSignals()

    def setupSignals(self):
        self.inputBandsBtn.clicked.connect(self.getInputBands)
        self.outputPathBtn.clicked.connect(self.getOutputFolder)
        self.algoUnsupervisedComboBox.currentTextChanged.connect(self.selectAlgorithm)
        self.runClassificationBtn.clicked.connect(self.runClassification)

    def getInputBands(self):
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self, "Select Band Images", "", "Raster Files (*.tif *.tiff);;All Files (*)"
        )
        if files:
            # Store files for later use
            self.selected_band_files = files

            # Join filenames into one string
            joined_paths = ";".join(files)

            # Display in QLineEdit
            self.inputBandsPathTxt.setText(joined_paths)

    def getOutputFolder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Output Folder", ""
        )
        if folder:
            self.output_folder = folder
            self.outputPathTxt.setText(folder)

    def selectAlgorithm(self, text):
        # Reset progress bar
        self.progressBar.setValue(0)
        # Show corresponding page in stacked widget
        if text == "Decision Tree":
            self.algoStkUnsupervised.setCurrentWidget(self.kmeansPage)
        # Add other algorithms if needed
        # elif text == "Random Forest":
        #     self.stackedWidget.setCurrentWidget(self.randomForestPage)
        else:
            self.algoStkUnsupervised.setCurrentIndex(0)

    def runClassification(self):
        try:
            self.progressBar.setValue(10)

            # Step 1: Stack bands
            preprocessor = DataPreprocessor(self.selected_band_files)
            image_array, meta = preprocessor.stack_bands()
            self.progressBar.setValue(30)

            # Step 2: Reshape image (H, W, B) → (H*W, B)
            h, w, b = image_array.shape
            flat_image = image_array.reshape(-1, b)
            flat_image = flat_image.astype(np.float32)

            # Optional: Remove NaNs if any
            valid_mask = ~np.isnan(flat_image).any(axis=1)
            valid_pixels = flat_image[valid_mask]

            self.progressBar.setValue(40)

            # Step 3: Read algorithm and parameters
            n_classes = self.noOfClassesSpinBox.value()
            algorithm_name = self.algoUnsupervisedComboBox.currentText()

            if algorithm_name == "K-Means":
                model = CustomKMeans(n_clusters=n_classes, random_state=42)
            else:
                QtWidgets.QMessageBox.critical(
                    self, "Error", f"Unsupported algorithm: {algorithm_name}"
                )
                return

            model.fit(valid_pixels)
            labels = model.classify(valid_pixels)

            self.progressBar.setValue(70)

            # Step 4: Prepare classified image with -1 where invalid
            classified_image = np.full(flat_image.shape[0], -1, dtype=np.int16)
            classified_image[valid_mask] = labels
            classified_image = classified_image.reshape(h, w)

            # Step 5: Write classified raster
            output_path = os.path.join(
                self.output_folder, "classified_unsupervised.tif"
            )
            output_meta = meta.copy()
            output_meta.update({"count": 1, "dtype": "int16"})

            with rasterio.open(output_path, "w", **output_meta) as dst:
                dst.write(classified_image, 1)

            self.progressBar.setValue(100)
            QtWidgets.QMessageBox.information(
                self, "Success", "Unsupervised classification completed!"
            )

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))
