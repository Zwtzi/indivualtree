import sys
import math
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QSlider, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class EnsembleWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Condorcet's Jury Theorem - Ensemble Trees")

        # Fondo claro y letras negras
        self.setStyleSheet("""
            background-color: #cce3c4;
            font-family: Arial;
            color: black;
        """)

        self.tree_count = 25
        self.tree_accuracy = 60

        # Ruta dinámica a la carpeta de imágenes
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.image_path = os.path.normpath(os.path.join(current_dir, "Imagenes"))

        self.layout = QVBoxLayout()

        # Cuadrícula visual para los árboles
        self.tree_grid_layout = QGridLayout()
        self.tree_widgets = []
        self.update_tree_visuals()

        # Slider para número de árboles
        self.tree_slider_label = QLabel(f"# of Trees: {self.tree_count}")
        self.tree_slider = QSlider(Qt.Orientation.Horizontal)
        self.tree_slider.setRange(1, 25)
        self.tree_slider.setSingleStep(2)
        self.tree_slider.setValue(self.tree_count)
        self.tree_slider.setPageStep(2)
        self.tree_slider.valueChanged.connect(self.update_tree_count)

        # Slider para precisión
        self.acc_slider_label = QLabel(f"Tree Accuracy: {self.tree_accuracy}%")
        self.acc_slider = QSlider(Qt.Orientation.Horizontal)
        self.acc_slider.setRange(50, 100)
        self.acc_slider.setValue(self.tree_accuracy)
        self.acc_slider.valueChanged.connect(self.update_tree_accuracy)

        # Gráfico
        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        # Añadir widgets al layout principal
        self.layout.addLayout(self.tree_grid_layout)
        self.layout.addWidget(self.tree_slider_label)
        self.layout.addWidget(self.tree_slider)
        self.layout.addWidget(self.acc_slider_label)
        self.layout.addWidget(self.acc_slider)
        self.layout.addWidget(self.canvas)

        self.setLayout(self.layout)
        self.plot_ensemble_accuracy()

    def update_tree_count(self, value):
        if value % 2 == 0:
            value += 1
        self.tree_count = value
        self.tree_slider.setValue(value)
        self.tree_slider_label.setText(f"# of Trees: {value}")
        self.update_tree_visuals()
        self.plot_ensemble_accuracy()

    def update_tree_accuracy(self, value):
        self.tree_accuracy = value
        self.acc_slider_label.setText(f"Tree Accuracy: {value}%")
        self.plot_ensemble_accuracy()

    def ensemble_accuracy(self, p, n):
        k = n // 2 + 1
        acc = sum(
            math.comb(n, i) * (p ** i) * ((1 - p) ** (n - i))
            for i in range(k, n + 1)
        )
        return acc

    def update_tree_visuals(self):
        # Limpiar widgets anteriores
        while self.tree_grid_layout.count():
            item = self.tree_grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        self.tree_widgets.clear()

        cols = 5
        for i in range(self.tree_count):
            row = i // cols
            col = i % cols

            label = QLabel()
            label.setFixedSize(30, 30)

            image_file = os.path.join(self.image_path, f"{i + 1}.png")
            pixmap = QPixmap(image_file)

            if not pixmap.isNull():
                pixmap = pixmap.scaled(30, 30, Qt.AspectRatioMode.IgnoreAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
                label.setPixmap(pixmap)
            else:
                label.setStyleSheet("background-color: #2e8b57; border: 1px solid #14532d;")

            self.tree_grid_layout.addWidget(label, row, col)
            self.tree_widgets.append(label)

    def plot_ensemble_accuracy(self):
        self.ax.clear()
        tree_acc = self.tree_accuracy / 100.0
        x_vals = list(range(1, self.tree_count + 1, 2))
        y_vals = [self.ensemble_accuracy(tree_acc, n) for n in x_vals]

        self.ax.plot(x_vals, y_vals, 'o-', color='gold', label="Ensemble Accuracy")
        for x, y in zip(x_vals, y_vals):
            self.ax.text(x, y, f"{y:.2f}", ha='center', va='bottom', fontsize=8)

        self.ax.set_ylim(0, 1.05)
        self.ax.set_xlim(0, self.tree_count + 1)
        self.ax.set_xticks(range(1, self.tree_count + 1, 2))
        self.ax.set_yticks([i / 10.0 for i in range(11)])
        self.ax.set_xlabel("Ensemble Accuracy by Tree Count")
        self.ax.set_ylabel("Accuracy")
        self.ax.set_title("Majority Voting with Multiple Trees")
        self.ax.grid(True)
        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EnsembleWidget()
    window.resize(700, 600)
    window.show()
    sys.exit(app.exec())
