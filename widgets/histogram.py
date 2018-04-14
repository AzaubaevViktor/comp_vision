import time
from math import log

import numpy as np
from PyQt5.QtGui import QPainter, QPen, QPixmap, QImage
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt

from utils import QColor
from .processing import qimageview


def timechecker(orig_func):
    def func(self, img: QImage):
        res = img.width() * img.height()
        print("======== Histogramm ==========")
        print("Res: {:.2f} Kpix".format(res / 1000))
        st = time.time()
        orig_func(self, img)
        tm = time.time() - st
        speed = res / tm
        print("Time: {:.2f}s".format(tm))
        print("Speed: {:.2f}Kpix/s".format(speed / 1000))
        self.speed = self.speed * 0.9 + speed * 0.1

    return func


class HistogramWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.r = [0] * 256
        self.g = [0] * 256
        self.b = [0] * 256
        self.initUI()
        self.speed = 100000

    def set_status(self, msg, sec=0):
        self.parent.status(msg, sec)

    def initUI(self):
        self.setMinimumSize(258, 16)

    @timechecker
    def calc_image(self, img: QImage):
        rgb = qimageview(img)
        self.set_status("Calculating histogram... {:.1f}".format(0))
        self.r = np.bincount(rgb[..., 0].flatten())
        self.set_status("Calculating histogram... {:.1f}".format(25))
        self.g = np.bincount(rgb[..., 1].flatten())
        self.set_status("Calculating histogram... {:.1f}".format(50))
        self.b = np.bincount(rgb[..., 2].flatten())
        self.set_status("Calculating histogram... {:.1f}".format(75))

        mx = max(max(self.r), max(self.g), max(self.b))

        self.r = np.log(self.r + 1) / log(mx + 1)
        self.g = np.log(self.g + 1) / log(mx + 1)
        self.b = np.log(self.b + 1) / log(mx + 1)

        if len(self.r) < 256:
            self.r = np.append(self.r, [0] * (256 - len(self.r)))
        if len(self.g) < 256:
            self.g = np.append(self.g, [0] * (256 - len(self.g)))
        if len(self.b) < 256:
            self.b = np.append(self.b, [0] * (256 - len(self.b)))

        self.r = list(self.r)
        self.g = list(self.g)
        self.b = list(self.b)


        self.set_status("Calculating histogram... {:.1f}".format(100))

        self.set_status("Ready")
        self.update()

    @timechecker
    def _calc_image(self, img: QImage):
        r = [0] * 256
        g = [0] * 256
        b = [0] * 256
        for x in range(img.width()):
            self.set_status("Calculating histogram... {:.1f}".format(
                x / img.width() * 100
            ))
            for y in range(img.height()):
                red, green, blue, a = img.pixelColor(x, y).getRgb()
                r[red] += 1
                g[green] += 1
                b[blue] += 1

        mx = max(max(r), max(g), max(b))

        for i in range(255):
            r[i] = log(r[i] + 1) / log(mx + 1)
            g[i] = log(g[i] + 1) / log(mx + 1)
            b[i] = log(b[i] + 1) / log(mx + 1)

        self.r = r
        self.g = g
        self.b = b

        self.set_status("Ready")
        self.update()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self._draw_widget(qp)
        qp.end()

    def _draw_widget(self, qp):
        size = self.size()
        w = size.width()
        h = size.height()

        qp.setBrush(QColor(0, 0, 0))

        qp.drawRect(0, 0, w - 1, h - 1)
        rc = QColor(255, 0, 0)
        gc = QColor(0, 255, 0)
        bc = QColor(0, 0, 255)

        for x in range(256):
            values = [(self.r[x], rc), (self.g[x], gc), (self.b[x], bc)]

            self._draw_v_line(qp, values, x + 1)

    def _draw_v_line(self, qp, values, pos_x):
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
            qp.drawLine(pos_x, (1 - start) * (self.height() - 3) + 1, pos_x, (1 - end) * (self.height() - 3) + 1)

