import sys
import os
import re
import time
import platform
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QCheckBox, QVBoxLayout,
    QHBoxLayout,QWidget, QMessageBox, QFrame, QPushButton, QToolButton,
    QSplashScreen, QTextEdit, QLineEdit, QComboBox, QSizePolicy,
    QTableView, QTableWidget, QTableWidgetItem, QTableWidgetSelectionRange,
    QHeaderView, QToolTip, QRadioButton, QButtonGroup, QGroupBox,
)
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtGui import (
    QIcon, QPixmap, QFont, QFontMetrics, QStandardItemModel, QStandardItem,
    QPainter, QGuiApplication, QCursor, 
)
from PySide6.QtCore import Qt, QTimer, QSize, QDateTime, QModelIndex
basedir = os.path.dirname(__file__)
from respick.respick.core import *
from respick.respick.cli import format_resistor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ResPick")
        system = platform.system()
        if system == "Windows":
            self.setWindowIcon(QIcon(os.path.join(basedir, "icons/icon.ico")))
        elif system == "Darwin":  # macOS
            self.setWindowIcon(QIcon(os.path.join(basedir, "icons/icon.svg")))
        elif system == "Linux":
            self.setWindowIcon(QIcon(os.path.join(basedir, "icons/icon.svg")))
        self.setMinimumSize(445, 300)
        self.resize(455, 507)
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Top layout with logo and title
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
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
        left_layout.addLayout(input_layout)

        self.rmin_label = QLabel("Rmin:")
        self.rmin_sel = QComboBox()
        self.rmin_sel.addItems(["0Ω", "100RΩ", "1kΩ", "10kΩ", "100kΩ", "1MΩ"])
        self.rmin_list = [0, 1E2, 1E3, 1E4, 1E5, 1E6]
        self.rmin_sel.setCurrentIndex(2)
        self.rmax_label = QLabel("Rmax:")
        self.rmax_sel = QComboBox()
        self.rmax_sel.addItems(["1kΩ", "10kΩ", "100kΩ", "1MΩ", "10MΩ", "100MΩ"])
        self.rmax_list = [1E3, 1E4, 1E5, 1E6, 1E7, 1E8]
        self.rmax_sel.setCurrentIndex(3)
        self.res_class = QComboBox()
        self.res_class_label = QLabel("Series:")
        self.res_class.addItems(["E12", "E24", "E96"])
        self.res_class.setCurrentIndex(1)

        range_layout.addWidget(self.rmin_label)
        range_layout.addWidget(self.rmin_sel)
        range_layout.addWidget(self.rmax_label)
        range_layout.addWidget(self.rmax_sel)
        range_layout.addWidget(self.res_class_label)
        range_layout.addWidget(self.res_class)
        range_layout.addStretch()
        left_layout.addLayout(range_layout)

        # radio buttons for fix R1 or R2
        self.radio1 = QRadioButton("No Fix")
        self.radio2 = QRadioButton("Fix R1")
        self.radio3 = QRadioButton("Fix R2")
        #button_group = QButtonGroup(self)
        #button_group.addButton(self.radio1)
        #button_group.addButton(self.radio2)
        #button_group.addButton(self.radio3)
        #button_group.setExclusive(True)

        self.radio1.setChecked(True)
        group = QGroupBox("")
        radio_layout = QHBoxLayout(group)
        radio_layout.addWidget(self.radio1)
        radio_layout.addWidget(self.radio2)
        radio_layout.addWidget(self.radio3)
        self.radio1.toggled.connect(self.on_radio1_clcked)
        self.radio2.toggled.connect(self.on_radio2_clcked)
        self.radio3.toggled.connect(self.on_radio3_clcked)

        fix_res_layout = QHBoxLayout()
        fix_res_layout.addWidget(group)

        self.fix_value_label = QLabel("value:")
        self.fix_value = QLineEdit()
        self.fix_value.setPlaceholderText("")
        self.res_lvlel_sel = QComboBox()
        self.res_lvlel_sel.addItems(["Ω", "kΩ", "MΩ"])
        self.res_lvlel_sel.setCurrentIndex(1)
        # set default not visible
        self.fix_value_label.setVisible(False)
        self.fix_value.setVisible(False)
        self.res_lvlel_sel.setVisible(False)
        self.fix_value_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.fix_value.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.res_lvlel_sel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        fix_res_layout.addWidget(self.fix_value_label)
        fix_res_layout.addWidget(self.fix_value)
        fix_res_layout.addWidget(self.res_lvlel_sel)
        left_layout.addLayout(fix_res_layout)

        self.result_table = QTableView()
        self.model = QStandardItemModel(3, 4)  # 4行3列
        self.model.setHorizontalHeaderLabels(['R1', 'R2', '输出电压(V)', '误差(V)'])
        self.result_table.setModel(self.model)
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.result_table.setSelectionBehavior(QTableView.SelectRows)
        self.result_table.setEditTriggers(QTableView.NoEditTriggers)
        self.result_table.doubleClicked.connect(self.on_table_double_clicked)

        # svg image to show diagram
        svg_widget = QSvgWidget(os.path.join(basedir, "img/respick_dcdc.svg"))
        svg_widget.setStyleSheet("background-color: black; border: 1px solid lightgray;")
        
        right_layout.addWidget(self.result_table)
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        main_layout.addWidget(svg_widget, alignment=Qt.AlignCenter)

    def pick_resistor(self):
        try:
            if self.vout_text.text() == '':
                vout = float(self.vout_text.placeholderText())
                self.vout_text.setText(self.vout_text.placeholderText())
            else:
                vout = float(self.vout_text.text())
            if self.vfb_text.text() == '':
                vfb = float(self.vfb_text.placeholderText())
                self.vfb_text.setText(self.vfb_text.placeholderText())
            else:
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
        if self.radio2.isChecked():
            # fix R1
            try:
                fix_r1_value = float(self.fix_value.text())
                fix_r1_level = self.res_lvlel_sel.currentIndex()
                fix_r1 = f"{fix_r1_value}" + {0: "R", 1: "k", 2: "M"}[fix_r1_level]
            except ValueError:
                QMessageBox.warning(self, "Warning", "Invalid fixed R1 value. Please enter a numeric value.")
                return
            results = find_best_divider(vout, vfb, rmin, rmax, self.res_class.currentText(), keep_r1=fix_r1)
        elif self.radio3.isChecked():
            # fix R2
            try:
                fix_r2_value = float(self.fix_value.text())
                fix_r2_level = self.res_lvlel_sel.currentIndex()
                fix_r2 = f"{fix_r2_value}" + {0: "R", 1: "K", 2: "M"}[fix_r2_level]
            except ValueError:
                QMessageBox.warning(self, "Warning", "Invalid fixed R2 value. Please enter a numeric value.")
                return
            results = find_best_divider(vout, vfb, rmin, rmax, self.res_class.currentText(), keep_r2=fix_r2)
        else:
            # no fix
            results = find_best_divider(vout, vfb, rmin, rmax, self.res_class.currentText())

        row_index = 0
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['R1', 'R2', '输出电压(V)', '误差(V)'])
        for r1, r2, vout, error in results:
            item = QStandardItem(f"{format_resistor(r1)}")
            self.model.setItem(row_index, 0, item)
            item = QStandardItem(f"{format_resistor(r2)}")
            self.model.setItem(row_index, 1, item)
            item = QStandardItem(f"{vout:.2f}")
            self.model.setItem(row_index, 2, item)
            item = QStandardItem(f"{error:.2f}")
            self.model.setItem(row_index, 3, item)
            row_index = row_index + 1
        self.result_table.setModel(self.model)

    def on_table_double_clicked(self, index: QModelIndex):
        """双击复制内容并提示。"""
        if not index.isValid():
            return

        text = index.data()

        # 复制到剪贴板
        QGuiApplication.clipboard().setText(text)

        # 在鼠标附近显示提示
        QToolTip.showText(QCursor.pos(), f"已复制: {text}", self.result_table)

    def on_radio1_clcked(self):
        self.fix_value_label.setVisible(False)
        self.fix_value.setVisible(False)
        self.res_lvlel_sel.setVisible(False)
        self.fix_value_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.fix_value.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.res_lvlel_sel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

    def on_radio2_clcked(self):
        self.fix_value_label.setVisible(True)
        self.fix_value.setVisible(True)
        self.res_lvlel_sel.setVisible(True)
        self.fix_value_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.fix_value.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.res_lvlel_sel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def on_radio3_clcked(self):
        self.fix_value_label.setVisible(True)
        self.fix_value.setVisible(True)
        self.res_lvlel_sel.setVisible(True)
        self.fix_value_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.fix_value.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.res_lvlel_sel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Splash screen
    splash_pix = QPixmap(os.path.join(basedir, "icons/respick_splash.png"))
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
