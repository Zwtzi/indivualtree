import sys
import os
import math
import random

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QSlider, QGridLayout,
    QPushButton, QHBoxLayout
)
from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPolygonF
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# === CLASE DEL WIDGET PRINCIPAL (DEMO) ===
class EnsembleWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Condorcet's Jury Theorem - Ensemble Trees")

        self.setStyleSheet("""
            background-color: #cce3c4;
            font-family: Arial;
            color: black;
        """)

        self.tree_count = 25
        self.tree_accuracy = 60

        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.image_path = os.path.normpath(os.path.join(current_dir, "Imagenes"))

        self.layout = QVBoxLayout()
        self.tree_grid_layout = QGridLayout()
        self.tree_widgets = []
        self.update_tree_visuals()

        self.tree_slider_label = QLabel(f"# of Trees: {self.tree_count}")
        self.tree_slider = QSlider(Qt.Orientation.Horizontal)
        self.tree_slider.setRange(1, 25)
        self.tree_slider.setSingleStep(2)
        self.tree_slider.setValue(self.tree_count)
        self.tree_slider.setPageStep(2)
        self.tree_slider.valueChanged.connect(self.update_tree_count)

        self.acc_slider_label = QLabel(f"Tree Accuracy: {self.tree_accuracy}%")
        self.acc_slider = QSlider(Qt.Orientation.Horizontal)
        self.acc_slider.setRange(50, 100)
        self.acc_slider.setValue(self.tree_accuracy)
        self.acc_slider.valueChanged.connect(self.update_tree_accuracy)

        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

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


# === CLASE DE ANIMACIÓN ===
class RandomForestAnimationWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bagging Animation - Random Forest")
        self.resize(800, 600)

        self.num_samples = 3
        self.num_points = 10
        self.points = []
        self.samples = []
        self.moving_points = []

        self.step_size = 0.05
        self.stage = 0  # Etapa actual

        # Temporizadores
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)

        self.story_timer = QTimer()
        self.story_timer.timeout.connect(self.next_stage)

        self.generate_data()
        self.animation_timer.start(30)

    def generate_data(self):
        self.points.clear()
        center_x = self.width() // 2
        center_y = 150
        radius = 120

        for i in range(self.num_points):
            shape = random.choice(["circle", "square", "triangle"])
            color = QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            size = random.randint(10, 20)
            angle = (2 * math.pi * i) / self.num_points
            start_x = center_x + radius * 0.7 * math.cos(angle)
            start_y = center_y + radius * 0.7 * math.sin(angle)
            self.points.append({
                "shape": shape,
                "color": color,
                "size": size,
                "x": start_x,
                "y": start_y
            })

        self.samples.clear()
        for _ in range(self.num_samples):
            sample = [random.choice(self.points) for _ in range(self.num_points)]
            self.samples.append(sample)

        self.moving_points.clear()
        sub_positions = [
            (center_x - 220, 380),
            (center_x,       380),
            (center_x + 220, 380)
        ]
        for idx, sample in enumerate(self.samples):
            cx, cy = sub_positions[idx]
            for i, point in enumerate(sample):
                angle = (2 * math.pi * i) / len(sample)
                target_x = cx + 60 * 0.7 * math.cos(angle)
                target_y = cy + 60 * 0.7 * math.sin(angle)
                self.moving_points.append({
                    "ref": point,
                    "x": point["x"],
                    "y": point["y"],
                    "target_x": target_x,
                    "target_y": target_y,
                    "done": False
                })

    def update_animation(self):
        all_done = True
        for p in self.moving_points:
            if p["done"]:
                continue
            dx = p["target_x"] - p["x"]
            dy = p["target_y"] - p["y"]
            dist = math.hypot(dx, dy)

            if dist < 1:
                p["x"], p["y"] = p["target_x"], p["target_y"]
                p["done"] = True
            else:
                p["x"] += dx * self.step_size
                p["y"] += dy * self.step_size
                all_done = False

        self.update()

        if all_done:
            self.animation_timer.stop()
            self.story_timer.start(3000)

    def next_stage(self):
        self.stage += 1
        if self.stage > 3:
            self.story_timer.stop()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center_x = self.width() // 2
        center_y = 150
        radius = 120

        # Etapa 0: Bagging Animation
        if self.stage == 0:
            painter.setPen(Qt.GlobalColor.darkGray)
            painter.setBrush(Qt.GlobalColor.transparent)
            painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
            for p in self.moving_points:
                self.draw_point(painter, p["ref"], p["x"], p["y"])

            sub_positions = [
                (center_x - 220, 380, "Sample 1"),
                (center_x,       380, "Sample 2"),
                (center_x + 220, 380, "Sample 3")
            ]
            for cx, cy, label in sub_positions:
                painter.setPen(Qt.GlobalColor.darkGray)
                painter.setBrush(Qt.GlobalColor.transparent)
                painter.drawEllipse(cx - 60, cy - 60, 120, 120)
                painter.setPen(Qt.GlobalColor.black)
                painter.drawText(cx - 30, cy + 80, label)

        # Etapa 1: Mostrar características
        elif self.stage == 1:
            painter.drawText(100, 120, "Features :)")
            features = [
                ("S", QColor("#ffe082"), "Size"),
                ("N", QColor("#ffcc80"), "# Sides"),
                ("C", QColor("#80cbc4"), "# Colors"),
                ("T", QColor("#f48fb1"), "Text or Symbol")
            ]
            for i, (abbr, color, label) in enumerate(features):
                painter.setBrush(color)
                painter.setPen(Qt.GlobalColor.black)
                painter.drawRect(100, 140 + i*40, 30, 30)
                painter.drawText(140, 160 + i*40, label)

            painter.setPen(Qt.GlobalColor.darkGray)
            painter.drawText(100, 320, "At each split, only a subset of these will be considered.")

        # Etapa 2: Primer split
        elif self.stage == 2:
            painter.setPen(Qt.GlobalColor.black)
            painter.drawText(100, 100, "First Split")
            painter.drawText(100, 130, "These three features are considered for the best split:")

            selected = [
                ("S", QColor("#ffe082")),
                ("C", QColor("#80cbc4")),
                ("T", QColor("#f48fb1"))
            ]
            for i, (abbr, color) in enumerate(selected):
                painter.setBrush(color)
                painter.drawRect(100 + i*40, 160, 30, 30)

        # Etapa 3: Árbol de decisiones
        elif self.stage == 3:
            painter.setPen(Qt.GlobalColor.black)
            painter.drawText(100, 100, "Decision Tree (Sample 1)")
            self.draw_tree(painter)

    def draw_point(self, painter, point, px, py):
        painter.setBrush(point["color"])
        painter.setPen(Qt.GlobalColor.black)
        size = point["size"]
        if point["shape"] == "circle":
            painter.drawEllipse(QPointF(px, py), size, size)
        elif point["shape"] == "square":
            painter.drawRect(int(px - size), int(py - size), int(size * 2), int(size * 2))
        elif point["shape"] == "triangle":
            triangle = QPolygonF([
                QPointF(px, py - size),
                QPointF(px - size, py + size),
                QPointF(px + size, py + size)
            ])
            painter.drawPolygon(triangle)

    def draw_tree(self, painter):
        # Dibujo básico de árbol
        nodes = [
            (300, 140, "C"),     # raíz
            (250, 200, "T"),     # izquierda
            (200, 260, "S"),     # izquierda-izquierda
            (160, 320, "No"),
            (240, 320, "Yes"),
            (350, 200, "T"),     # derecha
            (330, 260, "No"),
            (370, 260, "No")
        ]
        connections = [
            (0, 1), (1, 2), (2, 3), (2, 4),
            (0, 5), (5, 6), (5, 7)
        ]

        painter.setBrush(Qt.GlobalColor.white)
        for x, y, label in nodes:
            painter.drawEllipse(x - 15, y - 15, 30, 30)
            painter.drawText(x - 5, y + 5, label)

        for a, b in connections:
            x1, y1, _ = nodes[a]
            x2, y2, _ = nodes[b]
            painter.drawLine(x1, y1, x2, y2)


# === MENÚ VISUAL ===
class MenuInicial(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menú Principal")
        self.setStyleSheet("background-color: #e0f7fa; font-size: 16px; color: black;")
        layout = QVBoxLayout()

        label = QLabel("¿Qué quieres hacer?")
        layout.addWidget(label)

        btn_demo = QPushButton("1. Ejecutar Demo")
        btn_anim = QPushButton("2. Crear Animación")

        btn_demo.clicked.connect(self.abrir_demo)
        btn_anim.clicked.connect(self.abrir_animacion)

        btns_layout = QHBoxLayout()
        btns_layout.addWidget(btn_demo)
        btns_layout.addWidget(btn_anim)

        layout.addLayout(btns_layout)
        self.setLayout(layout)

    def abrir_demo(self):
        self.hide()
        self.demo = EnsembleWidget()
        self.demo.resize(700, 600)
        self.demo.show()

    def abrir_animacion(self):
        self.hide()
        self.animacion = RandomForestAnimationWidget()
        self.animacion.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    menu = MenuInicial()
    menu.resize(400, 150)
    menu.show()
    sys.exit(app.exec())
