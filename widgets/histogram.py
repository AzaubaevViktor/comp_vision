from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt

from utils import QColor


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

