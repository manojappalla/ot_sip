from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QColorDialog,
    QHeaderView,
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
import random


class SymbologyDialogDiscrete(QDialog):
    def __init__(self, class_values, current_colors=None):
        super().__init__()
        self.setWindowTitle("Symbology - Classified Data")
        self.resize(400, 300)

        self.class_values = class_values
        self.color_map = {}

        layout = QVBoxLayout()
        self.table = QTableWidget(len(class_values), 2)
        self.table.setHorizontalHeaderLabels(["Class", "Color"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        for i, val in enumerate(class_values):
            self.table.setItem(i, 0, QTableWidgetItem(str(val)))

            color = (
                current_colors[val]
                if current_colors and val in current_colors
                else QColor(*[random.randint(0, 255) for _ in range(3)])
            )
            self.color_map[val] = color

            btn = QPushButton()
            btn.setStyleSheet(f"background-color: {color.name()}")
            btn.clicked.connect(lambda _, v=val, b=btn: self.pick_color(v, b))
            self.table.setCellWidget(i, 1, btn)

        layout.addWidget(self.table)
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.accept)
        layout.addWidget(apply_btn)
        self.setLayout(layout)

    def pick_color(self, class_val, button):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_map[class_val] = color
            button.setStyleSheet(f"background-color: {color.name()}")

    def get_color_map(self):
        return self.color_map
