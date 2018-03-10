#!/usr/bin/python3
# -*- coding: utf-8 -*-
import random
import sys

import os

from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QAction, \
    qApp, QMainWindow, QFileDialog, QLabel, QHBoxLayout, QVBoxLayout


from widgets import ImageWidget, HistogramWidget

from utils import QColor



class Separator:
    pass


class Model:
    def __init__(self, prg):
        self.prg = prg
        self.pixmap = None

    def open_image(self, fname):
        self.pixmap = QPixmap(fname)


class Program(QMainWindow):
    def __init__(self, *size):
        super().__init__()
        self.model = Model(self)

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

        self.model.open_image(fname)

        self.program_widget.set_image(self.model.pixmap)

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
        self.coord = QLabel("Coord", self)
        self.pixel_rgb = QLabel('RGB', self)
        self.pixel_hsv = QLabel('HSV', self)

        self.image.selection_update.connect(self.selection_upd)

        hbox = QHBoxLayout()
        hbox.addWidget(self.image, 20)

        vbox = QVBoxLayout()
        vbox.addWidget(self.hist)
        vbox.addWidget(self.coord)
        vbox.addWidget(self.pixel_rgb)
        vbox.addWidget(self.pixel_hsv)

        hbox.addLayout(vbox, 1)

        self.setLayout(hbox)

    def selection_upd(self):
        img = self.image.selected.toImage()
        print(img.width(), img.height())

        coord = self.image.selection_img
        self.coord.setText("{}, {} x {}, {}".format(
            coord.left(), coord.top(),
            coord.right(), coord.bottom()
        ))

        if 1 == img.width() == img.height():
            pixel = QColor(img.pixel(0, 0))

            self.pixel_rgb.setText(
                "{}, {}, {}".format(pixel.red(), pixel.green(), pixel.blue())
            )

            self.pixel_hsv.setText(
                "{}, {}, {}".format(pixel.hue(), pixel.saturation(), pixel.value())
            )
        else:
            self.pixel_rgb.setText("Select one pixel")
            self.pixel_hsv.setText("Select one pixel")

        self.hist.setImage(img)

    def set_image(self, pixmap: QPixmap):
        self.image.setImage(pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    prg = Program(640, 480)
    sys.exit(app.exec_())
