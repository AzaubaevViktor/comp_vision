import time
from numpy import *
from PyQt5.QtGui import QPainter, QPen, QPixmap, QImage
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt

from utils import QColor


def timechecker(orig):
    def func(self, img: QImage):
        res = img.width() * img.height()
        print("==================")
        print("Res: {:.2f} Kpix".format(res / 1000))
        st = time.time()
        orig(self, img)
        tm = time.time() - st
        print("Time: {:.2f}s".format(tm))
        print("Speed: {:.2f}Kpix/s".format(res / 1000 / tm))
    return func


class HistogramWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.r = [0] * 256
        self.g = [0] * 256
        self.b = [0] * 256
        self.initUI()

    def initUI(self):
        self.setMinimumSize(258, 16)

    @timechecker
    def setImage(self, img: QImage):
        r = [0] * 256
        g = [0] * 256
        b = [0] * 256

        for x in range(img.width()):
            for y in range(img.height()):
                red, green, blue, a = img.pixelColor(x, y).getRgb()
                r[red] += 1
                g[green] += 1
                b[blue] += 1

        mx = max(max(r), max(g), max(b))

        for i in range(255):
            r[i] = log(r[i] + 1) / log(mx)
            g[i] = log(g[i] + 1) / log(mx)
            b[i] = log(b[i] + 1) / log(mx)

        self.r = r
        self.g = g
        self.b = b

        self.update()

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
            if isnan(end):
                end = 0
            if isnan(start):
                start = 0
            pen = QPen(color, 1, Qt.SolidLine)

            qp.setPen(pen)
            qp.drawLine(posX, (1 - start) * (self.height() - 3) + 1, posX, (1 - end) * (self.height() - 3) + 1)

