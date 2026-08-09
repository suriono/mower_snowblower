from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QFrame
)
from PySide6.QtCore import Qt


class LightIndicator(QWidget):
    def __init__(self, text="Status", size=60):
        super().__init__()

        # Label on top
        self.label = QLabel(text)
        self.label.setAlignment(Qt.AlignCenter)

        # Circular light
        self.light = QFrame()
        self.light.setFixedSize(size, size)
        self.light.setStyleSheet("border-radius: {0}px; background-color: gray;".format(size//2))

        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.light, alignment=Qt.AlignCenter)

    def set_green(self):
        self.light.setStyleSheet("border-radius: {0}px; background-color: green;".format(self.light.width()//2))

    def set_red(self):
        self.light.setStyleSheet("border-radius: {0}px; background-color: red;".format(self.light.width()//2))


# from PySide6.QtWidgets import QFrame

# class LightIndicator(QFrame):
#     def __init__(self, size=60):
#         super().__init__()
#         self.setFixedSize(size, size)
#         self.setStyleSheet("border-radius: {0}px; background-color: gray;".format(size//2))
#         self.set_red()  # Initially set to red

#     def set_green(self):
#         self.setStyleSheet("border-radius: {0}px; background-color: green;".format(self.width()//2))

#     def set_red(self):
#         self.setStyleSheet("border-radius: {0}px; background-color: red;".format(self.width()//2))

