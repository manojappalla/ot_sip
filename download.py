from PyQt5 import QtWidgets, uic
import sys
import ee
import io
import subprocess
import platform
from PyQt5.QtCore import QThread, pyqtSignal
from satimgproc.getgee import DownloaderManager


# Worker thread for Earth Engine authentication
class EEAthenticationThread(QThread):
    output_signal = pyqtSignal(str)  # Signal to send output text

    def run(self):
        """Runs Earth Engine authentication and captures output dynamically."""
        self.output_signal.emit("Starting Earth Engine authentication...\n")

        try:
            if platform.system() == "Windows":
                # Windows: Use `subprocess` without pexpect
                process = subprocess.Popen(
                    [
                        "python3",
                        "-c",
                        "import ee; ee.Authenticate(auth_mode='localhost')",
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    text=True,
                )

                # Read output line by line and forward to UI
                for line in iter(process.stdout.readline, ""):
                    self.output_signal.emit(line)

                for line in iter(process.stderr.readline, ""):
                    self.output_signal.emit(f"Error: {line}")

                process.wait()  # Wait for user to authenticate

            else:
                # Linux/macOS: Use `pexpect` to handle interactive prompts
                import pexpect

                child = pexpect.spawn(
                    "python3 -c 'import ee; ee.Authenticate(auth_mode=\"localhost\")'",
                    encoding="utf-8",
                    timeout=600,
                )

                while True:
                    try:
                        line = child.readline()
                        if not line:
                            break
                        self.output_signal.emit(line)
                    except pexpect.EOF:
                        break

                child.wait()

        except Exception as e:
            self.output_signal.emit(f"Exception: {e}\n")

        self.output_signal.emit("\nAuthentication process completed.\n")
        try:
            ee.Initialize(project="ee-remotesensingespace")
            self.output_signal.emit("Initialization process completed.\n")
        except Exception as e:
            self.output_signal.emit("\nError in Initialization.\n")


class DownloadWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Load UI dynamically
        uic.loadUi("ui/gee.ui", self)

        # Set up signals
        self.setupSignals()

        # Initialize authentication thread
        self.auth_thread = None

    def setupSignals(self):
        """Connect UI elements to their functions."""
        self.authenticateBtn.clicked.connect(self.authenticateGEE)
        self.geoJsonPathBtn.clicked.connect(self.selectGeoJson)
        self.downloadBtn.clicked.connect(self.downloadData)

    def downloadData(self):
        """Initiate the download process based on the selected satellite."""
        if self.landsatRBtn.isChecked():
            self.downloadProgressBar.setValue(0)
            download = DownloaderManager(
                dataset="landsat",
                geojson_path=self.geoJsonPath.text(),
                start_date=self.startDateSelector.date().toString("yyyy-MM-dd"),
                end_date=self.endDateSelector.date().toString("yyyy-MM-dd"),
            )
        elif self.sent2RBtn.isChecked():
            self.downloadProgressBar.setValue(0)
            download = DownloaderManager(
                dataset="sentinel",
                geojson_path=self.geoJsonPath.text(),
                start_date=self.startDateSelector.date().toString("yyyy-MM-dd"),
                end_date=self.endDateSelector.date().toString("yyyy-MM-dd"),
                cloud_cover=int(self.cloudCoverTxt.text()),
            )
        download.run()
        self.downloadProgressBar.setValue(100)

    def selectGeoJson(self):
        """Open a file dialog to select a GeoJSON file."""
        options = QtWidgets.QFileDialog.Options()
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select GeoJSON File",
            "",
            "GeoJSON Files (*.geojson)",
            options=options,
        )
        if fileName:
            self.geoJsonPath.setText(
                fileName
            )  # Update the text box with the selected file path

    def authenticateGEE(self):
        """Authenticate with Google Earth Engine and update the output text box."""

        # Disable button to prevent multiple clicks
        self.authenticateBtn.setEnabled(False)

        # Initialize authentication thread
        self.auth_thread = EEAthenticationThread()
        self.auth_thread.output_signal.connect(self.appendOutput)  # Connect signal
        self.auth_thread.start()  # Start the thread (calls `run()` internally)

    def appendOutput(self, text):
        """Append new output to the QTextEdit widget instead of replacing it."""
        self.authenticateConsoleOutput.appendPlainText(text)  # Append new text
        self.authenticateConsoleOutput.ensureCursorVisible()  # Auto-scroll to bottom

        # Re-enable the authenticate button after completion
        self.authenticateBtn.setEnabled(True)

        # Enable the download button after authentication
        self.downloadGroupBox.setEnabled(True)


# Run standalone if needed
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DownloadWindow()
    window.show()
    sys.exit(app.exec_())
