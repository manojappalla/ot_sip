import sys
import rasterio
import numpy as np
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QTreeWidgetItem,
    QMenu,
    QAction,
    QDialog,
    QVBoxLayout,
    QTextEdit,
)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from PyQt5 import uic
from download import DownloadWindow
from rs_indices import IndicesWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/sat_img_process.ui", self)

        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        self.layer_items = {}
        self.setupSignals()
        self.setupLayerTreeContextMenu()

    def setupSignals(self):
        self.actionOpen.triggered.connect(self.open_raster)
        self.layerTree.itemChanged.connect(self.handle_layer_visibility)
        self.actionDownload.triggered.connect(self.openDownloadWindow)
        self.actionIndices.triggered.connect(self.openIndicesWindow)

    def openDownloadWindow(self):
        self.downloadWindow = DownloadWindow()
        self.downloadWindow.show()

    def openIndicesWindow(self):
        """Opens the indices window."""
        self.indicesWindow = IndicesWindow()
        self.indicesWindow.show()

    def setupLayerTreeContextMenu(self):
        self.layerTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.layerTree.customContextMenuRequested.connect(self.show_layer_context_menu)

    def open_raster(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Raster", "", "Raster files (*.tif *.tiff)"
        )
        if not file_path or file_path in self.layer_items:
            return

        qimage = self.raster_to_qimage(file_path)
        if qimage is None:
            return

        pixmap = QPixmap.fromImage(qimage)
        item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(item)
        self.layer_items[file_path] = item

        layer_name = file_path.split("/")[-1]
        tree_item = self._make_tree_item(layer_name)
        self.layerTree.insertTopLevelItem(0, tree_item)
        self.update_z_values()

    def raster_to_qimage(self, path):
        try:
            with rasterio.open(path) as src:
                count = src.count
                if count >= 3:
                    r = src.read(1)
                    g = src.read(2)
                    b = src.read(3)
                    rgb = np.stack((r, g, b), axis=-1)
                    img = self._normalize(rgb)
                elif count == 1:
                    band = src.read(1)
                    norm = self._normalize(band)
                    img = np.stack((norm, norm, norm), axis=-1)
                else:
                    return None

                h, w, _ = img.shape
                qimg = QImage(img.data, w, h, 3 * w, QImage.Format_RGB888)
                return qimg
        except Exception as e:
            print("Error loading raster:", e)
            return None

    def _normalize(self, arr):
        arr = arr.astype(float)
        min_val, max_val = np.nanmin(arr), np.nanmax(arr)
        norm = ((arr - min_val) / (max_val - min_val + 1e-6)) * 255
        return norm.astype(np.uint8)

    def _make_tree_item(self, name):
        item = QTreeWidgetItem()
        item.setText(0, name)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(0, Qt.Checked)
        return item

    def show_layer_context_menu(self, pos):
        item = self.layerTree.itemAt(pos)
        if not item:
            return

        layer_name = item.text(0)
        menu = QMenu()
        zoom_action = QAction("Zoom to Layer", self)
        remove_action = QAction("Remove Layer", self)
        info_action = QAction("Information", self)
        menu.addAction(zoom_action)
        menu.addAction(remove_action)
        menu.addAction(info_action)

        action = menu.exec_(self.layerTree.viewport().mapToGlobal(pos))

        if action == remove_action:
            self.remove_layer(layer_name)
        elif action == zoom_action:
            self.zoom_to_layer(layer_name)
        elif action == info_action:
            self.show_layer_info(layer_name)

    def remove_layer(self, layer_name):
        path_to_remove = None
        for path in self.layer_items:
            if path.endswith(layer_name):
                path_to_remove = path
                break

        if path_to_remove:
            item = self.layer_items.pop(path_to_remove)
            self.scene.removeItem(item)

            for i in range(self.layerTree.topLevelItemCount()):
                tree_item = self.layerTree.topLevelItem(i)
                if tree_item.text(0) == layer_name:
                    self.layerTree.takeTopLevelItem(i)
                    break

        self.update_z_values()

    def zoom_to_layer(self, layer_name):
        for path, item in self.layer_items.items():
            if path.endswith(layer_name):
                bounds = item.boundingRect()
                margin_x = bounds.width() * 0.1
                margin_y = bounds.height() * 0.1
                expanded = bounds.adjusted(-margin_x, -margin_y, margin_x, margin_y)
                self.graphicsView.fitInView(expanded, Qt.KeepAspectRatio)
                break

    def handle_layer_visibility(self, item, column):
        layer_name = item.text(0)
        is_checked = item.checkState(0) == Qt.Checked

        for path, pixmap_item in self.layer_items.items():
            if path.endswith(layer_name):
                pixmap_item.setVisible(is_checked)
                break

    def update_z_values(self):
        total = self.layerTree.topLevelItemCount()
        for i in range(total):
            item = self.layerTree.topLevelItem(i)
            layer_name = item.text(0)
            for path, graphic_item in self.layer_items.items():
                if path.endswith(layer_name):
                    graphic_item.setZValue(total - i)
                    break

    def show_layer_info(self, layer_name):
        for path in self.layer_items:
            if path.endswith(layer_name):
                try:
                    with rasterio.open(path) as src:
                        meta = src.meta
                        metadata_str = "\n".join(f"{k}: {v}" for k, v in meta.items())
                        self.show_metadata_dialog(layer_name, metadata_str)
                except Exception as e:
                    self.show_metadata_dialog(
                        layer_name, f"Error reading metadata:\n{e}"
                    )
                break

    def show_metadata_dialog(self, title, message):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Metadata - {title}")
        layout = QVBoxLayout()
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(message)
        layout.addWidget(text_edit)
        dialog.setLayout(layout)
        dialog.resize(500, 400)
        dialog.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
