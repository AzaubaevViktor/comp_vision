#!/usr/bin/python3
# -*- coding: utf-8 -*-
import random
import sys

import os

from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QWidget, QAction, \
    qApp, QMainWindow, QFileDialog, QLabel, QHBoxLayout, QVBoxLayout, QSlider
from PyQt5.QtCore import Qt

from widgets import ImageWidget, HistogramWidget

from utils import QColor


class Separator:
    pass


class Program(QMainWindow):
    def __init__(self, *size):
        super().__init__()

        self._init_ui(size)

    def _init_ui(self, size):
        self._generate_menubar()
        self.setGeometry(100, 100, *size)

        self.setWindowTitle('Graphen')

        self.program_widget = ProgramWidget(self)
        self.setCentralWidget(self.program_widget)

        self.show()
        self.status("Ready")

    def _open(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', os.getcwd())[0]

        image = QImage(fname)

        self.program_widget.set_image(image)

    def _menubar_data(self):
        return [
            ('&File', [
                ('&Open', self._open),
                ("", Separator()),
                ('&Exit', {'triggered': qApp.quit, 'shortcut': 'Ctrl+Q', 'icon':None}),
            ]),
            ('&Other', [
                ('x', None),
                ('y', None),
            ]),
        ]

    def _generate_menubar(self):
        data = self._menubar_data()
        menubar = self.menuBar()

        for name, sub in data:
            menu = menubar.addMenu(name)
            self._generate_submenu(menu, sub)

    def _generate_submenu(self, menu, sub):
        for name, info in sub:
            action = None

            if callable(info):
                action = QAction(name, self)
                action.triggered.connect(info)
            elif isinstance(info, dict):
                action = QAction(QIcon(info['icon']), name, self)
                action.triggered.connect(info['triggered'])
                action.setShortcut(info['shortcut'])
            elif isinstance(info, Separator):
                menu.addSeparator()
            elif info is None:
                action = QAction(name, self)
            else:
                raise ValueError("`{}` may be callable/dict/None/list".format(info))

            if action:
                menu.addAction(action)

    def status(self, msg, sec=0):
        self.statusBar().showMessage(msg, sec)


class ProgramWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.image = ImageWidget()
        self.hist = HistogramWidget()
        self.coord = QLabel("", self)
        self.pixel_rgb = QLabel('', self)
        self.pixel_hsv = QLabel('', self)
        self.pixel_lab = QLabel('', self)
        self.h_slider = QSlider(Qt.Horizontal, self)
        self.s_slider = QSlider(Qt.Horizontal, self)
        self.v_slider = QSlider(Qt.Horizontal, self)

        self.h_slider.setMinimum(-180)
        self.h_slider.setMaximum(180)

        self.s_slider.setMinimum(-255)
        self.s_slider.setMaximum(255)

        self.v_slider.setMinimum(-255)
        self.v_slider.setMaximum(255)

        self._set_default()

        self.image.selection_update.connect(self.selection_upd)
        self.h_slider.valueChanged[int].connect(self.slider_update)
        self.s_slider.valueChanged[int].connect(self.slider_update)
        self.v_slider.valueChanged[int].connect(self.slider_update)

        hbox = QHBoxLayout()
        hbox.addWidget(self.image, 20)

        vbox = QVBoxLayout()
        vbox.addWidget(self.hist)
        vbox.addWidget(self.coord)
        vbox.addWidget(self.pixel_rgb)
        vbox.addWidget(self.pixel_hsv)
        vbox.addWidget(self.pixel_lab)

        h_slider_box = QHBoxLayout()
        h_slider_box.addWidget(QLabel("H:", self))
        h_slider_box.addWidget(self.h_slider)
        vbox.addLayout(h_slider_box)

        s_slider_box = QHBoxLayout()
        s_slider_box.addWidget(QLabel("S:", self))
        s_slider_box.addWidget(self.s_slider)
        vbox.addLayout(s_slider_box)

        v_slider_box = QHBoxLayout()
        v_slider_box.addWidget(QLabel("V:", self))
        v_slider_box.addWidget(self.v_slider)
        vbox.addLayout(v_slider_box)

        hbox.addLayout(vbox, 1)

        self.setLayout(hbox)

    def _set_default(self):
        self.coord.setText("Select pixel")
        self.pixel_rgb.setText("Select pixel")
        self.pixel_hsv.setText("Select pixel")
        self.pixel_lab.setText("Select pixel")

        self.h_slider.setValue(0)

    def slider_update(self):
        self.image.shift_hue = self.h_slider.value()
        self.image.shift_saturation = self.s_slider.value()
        self.image.shift_value = self.v_slider.value()

    def selection_upd(self):
        img = self.image.selected
        print(img.width(), img.height())

        coord = self.image.selection_img
        self.coord.setText("{}, {} x {}, {}".format(
            coord.left(), coord.top(),
            coord.right(), coord.bottom()
        ))

        if 1 == img.width() == img.height():
            pixel = QColor(img.pixel(0, 0))

            self.pixel_rgb.setText(
                "R:{}, G:{}, B:{}".format(pixel.red(), pixel.green(), pixel.blue())
            )

            self.pixel_hsv.setText(
                "H:{}, S:{}, V:{}".format(pixel.hue(), pixel.saturation(), pixel.value())
            )

            self.pixel_lab.setText(
                "L:{:.1f}, A:{:.1f}, B:{:.1f}".format(*pixel.lab())
            )
        else:
            self.pixel_rgb.setText("Select one pixel")
            self.pixel_hsv.setText("Select one pixel")
            self.pixel_lab.setText("Select one pixel")

        self.hist.setImage(img)

    def set_image(self, image: QImage):
        self.image.set_image(image)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    prg = Program(640, 480)
    sys.exit(app.exec_())
