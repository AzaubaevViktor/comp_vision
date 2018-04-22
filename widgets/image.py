import time

from PyQt5 import QtGui

from PyQt5.QtCore import QObject, pyqtSignal, QRect, QPoint, Qt
from PyQt5.QtGui import QPainter, QPixmap, QImage
from PyQt5.QtWidgets import QWidget

from utils import QColor, hsv_ranged
from .processing import shift_hsv, rgb_to_hsv, gaussian


class Communicate(QObject):

    selection_update = pyqtSignal()


class ImageWidget(QWidget):
    def __init__(self, parent):
        super().__init__()

        self.parent = parent

        self.imageOrigin: QImage = None
        self._rescaled_image: QImage = None
        self._shifted_image: QImage = None
        self._image: QImage = None

        self.selection: QRect = None
        self.selection_img: QRect = None
        self.coef = None

        self._filter_id = 0
        self._filter_args = tuple()

        self._communicate = Communicate()

        self.selection_update = self._communicate.selection_update

        self._init_ui()

        self.endMouse = True

        self._shift_hsv_values = [0, 0, 0]
    
    def set_status(self, msg, sec=0):
        self.parent.status(msg, sec)

    @property
    def shift_hsv(self):
        return tuple(self._shift_hsv_values)

    @shift_hsv.setter
    def shift_hsv(self, value):
        if len(value) != 3:
            raise ValueError("Shift_hsv may be 3 int!")
        self._shift_hsv_values = list(value)

        self._do_shift_hsv()
        self._apply_filter()
        self.update()

    def _do_shift_hsv(self):
        if self._rescaled_image is None:
            return

        if self._shift_hsv_values == [0, 0, 0]:
            self._shifted_image = self._rescaled_image
            return

        res = self._rescaled_image.width() * self._rescaled_image.height()
        print("========= HSV Shift =========")
        print("Res: {:.2f} Kpix".format(res / 1000))
        st = time.time()
        x = None
        for x in shift_hsv(self._rescaled_image, *self._shift_hsv_values):
            if isinstance(x, int):
                self.set_status("Recalc HSV {:.1f}%".format(
                    x * 100
                ))

        self._shifted_image: QImage = x

        tm = time.time() - st
        print("Time: {:.2f}s".format(tm))
        print("Speed: {:.2f}Kpix/s".format(res / 1000 / tm))

    def set_filter(self, filter_id, *args):
        self._filter_id = filter_id
        self._filter_args = args
        self._apply_filter()
        self.update()

    def _apply_filter(self):
        if self._filter_id == 1:
            sigma = self._filter_args[0]
            self._image = gaussian(self._shifted_image, sigma)
        else:
            self._image = self._shifted_image

    def get_image(self, is_selected, colors):
        if colors not in ["RGB", "HSV"]:
            raise ValueError("RGB, HSV, not `{}`".format(colors))

        if is_selected:
            img = self.selected_origin
        else:
            img = self.imageOrigin.copy()

        for x in shift_hsv(img, *self._shift_hsv_values):
            self.set_status("Saving: Recalc HSV {:.1f}%".format(
                x / img.width() * 100
            ))

        if colors == "RGB":
            return img

        if colors == "HSV":
            for x in rgb_to_hsv(img):
                self.set_status("Saving: Convert to HSV {:.1f}%".format(
                    x / img.width() * 100
                ))
            return img

    def to_image_rect(self, rect: QRect) -> QRect:
        rect = QRect(rect)
        if rect.top() > rect.bottom():
            _top, _bottom = rect.top(), rect.bottom()
            rect.setBottom(_top), rect.setTop(_bottom)

        if rect.left() > rect.right():
            _left, _right = rect.left(), rect.right()
            rect.setLeft(_right)
            rect.setRight(_left)

        return QRect(
            self.to_image_coord(rect.topLeft()),
            self.to_image_coord(rect.bottomRight())
        )

    def to_image_coord(self, point: QPoint) -> QPoint:
        return QPoint(point.x() * self.coef, point.y() * self.coef)

    def from_image_rect(self, rect: QRect) -> QRect:
        return QRect(
            self.from_image_coord(rect.topLeft()),
            self.from_image_coord(rect.bottomRight())
        )

    def from_image_coord(self, point: QPoint) -> QPoint:
        return QPoint(point.x() / self.coef, point.y() / self.coef)

    def _init_ui(self):
        self.setMinimumSize(10, 10)

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self._draw_widget(e, qp)
        qp.end()

    def resizeEvent(self, event: QtGui.QResizeEvent):
        self._rescale()
        self._do_shift_hsv()
        self._apply_filter()
        self.update()

    def _draw_widget(self, event, qp):
        qp.setBrush(QColor(0, 0, 0))
        qp.setPen(QColor(0, 0, 0))

        if self.imageOrigin is None:
            qp.drawText(event.rect(), Qt.AlignCenter, "No image")
        else:
            qp.drawImage(0, 0, self._image)

            self._draw_selection(qp)

    def _draw_selection(self, qp):
        if self.selection is None:
            return
        pen = QColor(0, 0, 255, 128)
        qp.setPen(pen)
        brush = QColor(0, 0, 128, 128)
        qp.setBrush(brush)
        qp.drawRect(self.selection)

    def _rescale(self):
        if self.imageOrigin is None:
            return

        if self.imageOrigin.height() == 0 or self.imageOrigin.width() == 0:
            self.imageOrigin = None
            return

        self.set_status("Rescaling...")

        aspect = self.width() / self.height()

        aspect_image = self.imageOrigin.width() / self.imageOrigin.height()

        if aspect_image > aspect:
            self.coef = self.imageOrigin.width() / self.width()
            _image = self.imageOrigin.scaledToWidth(self.width())
        else:
            self.coef = self.imageOrigin.height() / self.height()
            _image = self.imageOrigin.scaledToHeight(self.height())

        if self.selection is not None:
            self.selection = self.from_image_rect(self.selection_img)

        self._rescaled_image = _image

        self.set_status("Ready")

    def set_image(self, image: QImage):
        self.imageOrigin = image
        self.selection = None
        self.coef = None
        self._rescale()
        self._do_shift_hsv()
        self._apply_filter()
        self.update()

    def mousePressEvent(self, event):
        if self.imageOrigin is None:
            return
        if event.button() == Qt.LeftButton:
            self.selection = QRect(event.pos(), event.pos())
            self.selection_img = self.to_image_rect(self.selection)
            self.endMouse = False
            self.selection_update.emit()
        self.update()

    def mouseMoveEvent(self, event):
        if self.imageOrigin is None:
            return
        if event.buttons() == Qt.LeftButton:
            self.selection.setBottomRight(event.pos())
            self.selection_img = self.to_image_rect(self.selection)
            self.selection_update.emit()
        self.update()

    def mouseReleaseEvent(self, event):
        if self.imageOrigin is None:
            return
        if event.button() == Qt.LeftButton:
            self.selection.setBottomRight(event.pos())
            self.selection_img = self.to_image_rect(self.selection)
            self.endMouse = True
            self.selection_update.emit()
        self.update()

    @property
    def selected_origin(self) -> QImage:
        return self.imageOrigin.copy(self.selection_img)

    def selected(self, speed) -> QImage:
        img = self.selected_origin

        need = speed / 30
        resolution = img.height() * img.width()

        if self.endMouse or resolution < need:
            return img
        else:
            coef = (resolution / need) ** 0.5
            return img.scaled(img.width() / coef, img.height() / coef)
