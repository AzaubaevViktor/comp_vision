#!/usr/bin/python3
# -*- coding: utf-8 -*-
import random
import sys

import os
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QFont, QColor as _QColor, QPen
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QAction, \
    qApp, QMainWindow, QFileDialog, QLabel, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt


class QColor(_QColor):
    def __add__(self, other: "QColor"):
        return QColor(
            self.red() + other.red(),
            self.green() + other.green(),
            self.blue() + other.blue()
        )

    def __str__(self):
        if self.spec() == self.Rgb:
            return "<QColor {}, {}, {}>".format(
                self.green(),
                self.red(),
                self.blue()
            )

        return super().__str__()


class Separator:
    pass


class Model:
    def __init__(self, prg):
        self.prg = prg


class Program(QMainWindow):
    def __init__(self, *size):
        super().__init__()
        self.model = Model(self)

        self._init_ui(size)

    def _init_ui(self, size):
        self._generate_menubar()
        self.setGeometry(300, 300, *size)

        self.setWindowTitle('Graphen')

        self.program_widget = ProgramWidget(self)
        self.setCentralWidget(self.program_widget)

        self.show()
        self.status("Ready")

    def _open(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', os.getcwd())[0]

        self.model.open_image(fname)

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

    def mousePressEvent(self, event):
        print(event.pos(), event.button())

    def mouseMoveEvent(self, event):
        pass

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.drawText(event, qp)
        qp.end()

    def drawText(self, event, qp):
        qp.setPen(Qt.red)
        size = self.size()

        for i in range(1000):
            x = random.randint(1, size.width() - 1)
            y = random.randint(1, size.height() - 1)
            qp.drawPoint(x, y)


class HistogramWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.r = [x / 256 for x in range(256)]
        self.g = [1 - x / 256 for x in range(256)]
        self.b = [0.5 + x / 1024 for x in range(256)]
        self.initUI()

    def initUI(self):
        self.setMinimumSize(258, 16)

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    def drawWidget(self, qp):
        size = self.size()
        w = size.width()
        h = size.height()

        qp.setBrush(QColor(0, 0, 0))

        qp.drawRect(0, 0, w - 1, h - 1)
        rc = QColor(255, 0, 0)
        bc = QColor(0, 255, 0)
        gc = QColor(0, 0, 255)

        for x in range(256):
            values = [(self.r[x], rc), (self.g[x], gc), (self.b[x], bc)]

            self._drawVLine(qp, values, x + 1)

    def _drawVLine(self, qp, values, posX):
        values.sort(key=lambda item: item[0])

        first = values[0][1] + values[1][1] + values[2][1]
        second = values[1][1] + values[2][1]
        third = values[2][1]

        colors = [first, second, third]

        lines = [(0, values[0][0]), (values[0][0], values[1][0]), (values[1][0], values[2][0])]

        qp.setBrush(Qt.NoBrush)
        for (start, end), color in zip(lines, colors):
            pen = QPen(color, 1, Qt.SolidLine)

            qp.setPen(pen)
            qp.drawLine(posX, (1 - start) * (self.height() - 3) + 1, posX, (1 - end) * (self.height() - 3) + 1)


class ProgramWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.canvas = QLabel('Open image', self)
        self.hist = HistogramWidget()
        self.pixel_rgb = QLabel('RGB', self)
        self.pixel_hsv = QLabel('HSV', self)

        hbox = QHBoxLayout()
        hbox.addWidget(self.canvas)
        hbox.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addWidget(self.hist)
        vbox.addWidget(self.pixel_rgb)
        vbox.addWidget(self.pixel_hsv)

        hbox.addLayout(vbox)

        self.setLayout(hbox)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    prg = Program(640, 480)
    sys.exit(app.exec_())
