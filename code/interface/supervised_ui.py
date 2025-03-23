from PyQt5 import QtWidgets, uic
from satimgproc.classify import DataPreprocessor, DecisionTree, AccuracyAssessor
import rasterio
import geopandas as gpd
import os
import sys
import numpy as np


class SupervisedDialog(QtWidgets.QDialog):

    def __init__(self):
        super().__init__()

        # Load UI dynamically
        uic.loadUi("ui/supervised.ui", self)

        # Set up signals
        self.setupSignals()

    def setupSignals(self):
        self.inputBandsBtn.clicked.connect(self.getInputBands)
        self.inputShpBtn.clicked.connect(self.getShapeFile)
        self.outputPathBtn.clicked.connect(self.getOutputFolder)
        self.algoComboBox.currentTextChanged.connect(self.selectAlgorithm)
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

    def getShapeFile(self):
        file, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Shapefile", "", "Shapefiles (*.shp);;All Files (*)"
        )
        if file:
            self.selected_shapefile = file
            self.inputShpTxt.setText(file)
            # Read shapefile
            gdf = gpd.read_file(file)
            # Clear old items
            self.selectClassAttrList.clear()
            # Add attribute field names (exclude geometry column)
            for column in gdf.columns:
                if column != gdf.geometry.name:
                    self.selectClassAttrList.addItem(column)

    def getOutputFolder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Output Folder", ""
        )
        if folder:
            self.output_folder = folder
            self.outputPathTxt.setText(folder)

    def selectAlgorithm(self, text):
        # Reset progress bar
        self.progressBarSupervised.setValue(0)
        self.accuracyTxt.setPlainText("")
        # Show corresponding page in stacked widget
        if text == "Decision Tree":
            self.algoStk.setCurrentWidget(self.decisionTreePage)
        # Add other algorithms if needed
        # elif text == "Random Forest":
        #     self.stackedWidget.setCurrentWidget(self.randomForestPage)
        else:
            self.algoStk.setCurrentIndex(0)

    def runClassification(self):
        try:
            self.progressBarSupervised.setValue(0)

            # Step 1: Stack bands and extract training data
            preprocessor = DataPreprocessor(
                band_paths=self.selected_band_files,
                shapefile_path=self.selected_shapefile,
                class_attribute=self.selectClassAttrList.currentItem().text(),
            )
            image_array, meta = preprocessor.stack_bands()

            self.progressBarSupervised.setValue(30)

            X_train, X_test, y_train, y_test = preprocessor.extract_training_data()

            self.progressBarSupervised.setValue(50)

            algorithm = self.algoComboBox.currentText()

            if algorithm == "Decision Tree":
                # Step 2: Read parameters
                criterion = (
                    self.decisionTreeCriterionComboBox.currentText().lower() or "gini"
                )
                max_depth = self.decisionTreeMaxDepthSpinBox.value()
                if max_depth <= 0:
                    max_depth = None
                min_samples_split = self.minSamplesSplitSpinBox.value()
                if min_samples_split < 2:
                    min_samples_split = 2

                # Step 3: Train classifier
                classifier = DecisionTree(
                    criterion=criterion,
                    max_depth=max_depth,
                    min_samples_split=min_samples_split,
                )
                classifier.train(X_train, y_train)
                y_pred = classifier.predict(X_test)

            self.progressBarSupervised.setValue(80)

            # Step 4: Accuracy assessment
            assessor = AccuracyAssessor(y_test, y_pred)
            results = assessor.report()

            # Step 5: Show results
            report_lines = [
                f"Overall Accuracy: {results['overall_accuracy']:.3f}",
                f"Kappa Coefficient: {results['kappa']:.3f}",
                "",
            ]
            for i, (pa, ua) in enumerate(
                zip(results["producer_accuracy"], results["user_accuracy"])
            ):
                report_lines.append(
                    f"Class {i}: Producer Accuracy = {pa:.2f}, User Accuracy = {ua:.2f}"
                )

            print("\n".join(report_lines))
            self.accuracyTxt.setPlainText("\n".join(report_lines))

            # Step 6: Classify full image
            h, w, b = image_array.shape
            flat_pixels = image_array.reshape(-1, b)
            flat_predictions = classifier.predict(flat_pixels)
            classified_image = flat_predictions.reshape(h, w)

            self.progressBarSupervised.setValue(90)

            # Step 7: Save output
            output_path = os.path.join(self.output_folder, "classified_output.tif")
            meta.update(
                {
                    "count": 1,
                    "dtype": "uint8",
                    "compress": "lzw",
                }
            )
            with rasterio.open(output_path, "w", **meta) as dst:
                dst.write(classified_image.astype("uint8"), 1)

            self.progressBarSupervised.setValue(100)

        except Exception as e:
            exc_type, exc_obj, tb = sys.exc_info()
            fname = tb.tb_frame.f_code.co_filename
            func_name = tb.tb_frame.f_code.co_name
            line = tb.tb_lineno
            error_msg = (
                f"Error: {e}\nFile: {fname}\nFunction: {func_name}\nLine: {line}"
            )
            self.accuracyTxt.setPlainText(error_msg)
            self.progressBarSupervised.setValue(0)
