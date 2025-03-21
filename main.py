from PyQt5 import QtWidgets, uic
import sys
from download import DownloadWindow
from rs_indices import IndicesWindow


class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Load `sip.ui` dynamically
        uic.loadUi("ui/main.ui", self)

        # Connect the Download button to open `DownloadWindow`
        self.downloadBtnMainWindow.clicked.connect(self.openDownloadWindow)
        self.indicesBtnMainWindow.clicked.connect(self.openIndicesWindow)

    def openDownloadWindow(self):
        """Opens the download window."""
        self.downloadWindow = DownloadWindow()
        self.downloadWindow.show()
    
    def openIndicesWindow(self):
        """Opens the indices window."""
        self.indicesWindow = IndicesWindow()
        self.indicesWindow.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
