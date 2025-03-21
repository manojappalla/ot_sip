from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QColorDialog,
    QHeaderView,
)
from PyQt5.QtGui import QColor
import numpy as np


class SymbologyDialogContinuous(QDialog):
    def __init__(self, min_val, max_val, num_classes=4):
        super().__init__()
        self.setWindowTitle("Symbology - Continuous Data")
        self.resize(400, 300)

        self.min_val = min_val
        self.max_val = max_val
        self.num_classes = num_classes
        self.ranges = []
        self.color_map = []

        layout = QVBoxLayout()

        # Class count spinner
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Number of Classes:"))
        self.class_spinner = QSpinBox()
        self.class_spinner.setMinimum(2)
        self.class_spinner.setMaximum(10)
        self.class_spinner.setValue(num_classes)
        self.class_spinner.valueChanged.connect(self.build_table)
        top_layout.addWidget(self.class_spinner)
        layout.addLayout(top_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["From", "To", "Color"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        # Buttons
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.accept)
        layout.addWidget(self.apply_button)

        self.setLayout(layout)
        self.build_table(num_classes)

    def build_table(self, n):
        self.table.setRowCount(n)
        self.ranges = []
        self.color_map = []

        step = (self.max_val - self.min_val) / n
        for i in range(n):
            start = self.min_val + i * step
            end = start + step if i < n - 1 else self.max_val
            self.ranges.append((start, end))

            self.table.setItem(i, 0, QTableWidgetItem(f"{start:.2f}"))
            self.table.setItem(i, 1, QTableWidgetItem(f"{end:.2f}"))

            color = QColor.fromHsv(int(360 * i / n), 255, 200)
            self.color_map.append(color)
            color_btn = QPushButton()
            color_btn.setStyleSheet(f"background-color: {color.name()}")
            color_btn.clicked.connect(lambda _, row=i: self.pick_color(row))
            self.table.setCellWidget(i, 2, color_btn)

    def pick_color(self, row):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_map[row] = color
            btn = self.table.cellWidget(row, 2)
            btn.setStyleSheet(f"background-color: {color.name()}")

    def get_ranges_and_colors(self):
        return self.ranges, self.color_map
