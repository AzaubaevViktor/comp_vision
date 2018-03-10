#!/usr/bin/python3
# -*- coding: utf-8 -*-
import random
import sys

import os

from PyQt5.QtGui import QIcon, QPixmap, QPainter
from PyQt5.QtWidgets import QApplication, QWidget, QAction, \
    qApp, QMainWindow, QFileDialog, QLabel, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt

from widgets import ImageWidget, HistogramWidget




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

        self.canvas = ImageWidget()
        self.hist = HistogramWidget()
        self.pixel_rgb = QLabel('RGB', self)
        self.pixel_hsv = QLabel('HSV', self)

        hbox = QHBoxLayout()
        hbox.addWidget(self.canvas, 20)

        vbox = QVBoxLayout()
        vbox.addWidget(self.hist)
        vbox.addWidget(self.pixel_rgb)
        vbox.addWidget(self.pixel_hsv)

        hbox.addLayout(vbox, 1)

        self.setLayout(hbox)

    def set_image(self, pixmap: QPixmap):
        self.canvas.setImage(pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    prg = Program(640, 480)
    sys.exit(app.exec_())
