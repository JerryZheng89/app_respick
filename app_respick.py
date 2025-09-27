import sys
import os
import re
import time
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QCheckBox, QVBoxLayout,
    QHBoxLayout,QWidget, QMessageBox, QFrame, QPushButton, QToolButton,
    QSplashScreen, QTextEdit, QLineEdit, QComboBox, QSizePolicy
)
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtGui import QIcon, QPixmap, QFont, QFontMetrics
from PySide6.QtCore import Qt, QTimer, QSize, QDateTime
basedir = os.path.dirname(__file__)
from respick.core import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Path ResPicker")
        self.setWindowIcon(QIcon(os.path.join(basedir, "icons/icon.svg")))
        self.setMinimumSize(400, 300)
        self.resize(600, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Top layout with logo and title
        input_layout = QHBoxLayout()
        range_layout = QHBoxLayout()
        fm = QFontMetrics(self.font())

        self.vout_label = QLabel("Vout(V):")
        self.vout_text = QLineEdit()
        self.vout_text.setPlaceholderText("3.3")
        self.vout_text.setFixedWidth(fm.boundingRect("00.00").width() + 3)
        self.vfb_label = QLabel("Vfb(V):")
        self.vfb_text = QLineEdit()
        self.vfb_text.setPlaceholderText("0.6")
        self.vfb_text.setFixedWidth(fm.boundingRect("0.000").width() + 3)
        self.pick_button = QPushButton("Pick Resistor")
        self.pick_button.clicked.connect(self.pick_resistor)
        input_layout.addWidget(self.vout_label)
        input_layout.addWidget(self.vout_text)
        input_layout.addWidget(self.vfb_label)
        input_layout.addWidget(self.vfb_text)
        input_layout.addStretch()
        input_layout.addWidget(self.pick_button)
        main_layout.addLayout(input_layout)

        self.rmin_label = QLabel("Rmin:")
        self.rmin_sel = QComboBox()
        self.rmin_sel.addItems(["0Ω", "100RΩ", "1kΩ", "10kΩ", "100kΩ", "1MΩ"])
        self.rmin_list = [0, 1E2, 1E3, 1E4, 1E5, 1E6]
        self.rmin_sel.setCurrentIndex(0)
        self.rmax_label = QLabel("Rmax:")
        self.rmax_sel = QComboBox()
        self.rmax_sel.addItems(["1kΩ", "10kΩ", "100kΩ", "1MΩ", "10MΩ", "100MΩ"])
        self.rmax_list = [1E3, 1E4, 1E5, 1E6, 1E7, 1E8]
        self.rmax_sel.setCurrentIndex(3)
        range_layout.addWidget(self.rmin_label)
        range_layout.addWidget(self.rmin_sel)
        range_layout.addWidget(self.rmax_label)
        range_layout.addWidget(self.rmax_sel)
        range_layout.addStretch()
        main_layout.addLayout(range_layout)

    
    def pick_resistor(self):
        if self.vout_text.text() == "" or self.vfb_text.text() == "":
            QMessageBox.warning(self, "Warning", "Please enter both Vout and Vfb values.")
            return
        try:
            vout = float(self.vout_text.text())
            vfb = float(self.vfb_text.text())
        except ValueError:
            QMessageBox.warning(self, "Warning", "Invalid input. Please enter numeric values.")
            return
        rmin_index = self.rmin_sel.currentIndex()
        rmax_index = self.rmax_sel.currentIndex()
        rmin = self.rmin_list[rmin_index]
        rmax = self.rmax_list[rmax_index]
        if rmin >= rmax:
            QMessageBox.warning(self, "Warning", "Rmin should be less than Rmax.")
            return
        results = find_best_divider(vout, vfb, rmin, rmax, 'E24')
        result_str = "\n".join([f"R1: {r1} Ω, R2: {r2} Ω, Vout: {vout:.2f} V, Error: {error:.2f} V" 
                                for r1, r2, vout, error in results])
        QMessageBox.information(self, "Best Resistor Pairs", result_str)
        # QMessageBox.information(self, "Info", "Resistor picking logic goes here.")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Splash screen
    splash_pix = QPixmap(os.path.join(basedir, "icons/splash.png"))
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    #app.processEvents()

    # Simulate loading
    time.sleep(1)  # Simulate some loading time

    window = MainWindow()
    window.show()
    splash.finish(window)

    sys.exit(app.exec())
