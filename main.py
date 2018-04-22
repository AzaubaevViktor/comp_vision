#!/usr/bin/python3
# -*- coding: utf-8 -*-
import random
import sys

import os
from typing import Tuple

from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QWidget, QAction, \
    qApp, QMainWindow, QFileDialog, QLabel, QHBoxLayout, QVBoxLayout, QSlider, QMenu, QBoxLayout
from PyQt5.QtCore import Qt

from widgets import ImageWidget, HistogramWidget

from utils import QColor
from widgets.processing import shift_hsv


class Separator:
    pass


class Program(QMainWindow):
    instance = None

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

    def _save_generator(self, *args):
        def _():
            self._save_to(*args)

        return _

    def _save_to(self, is_selected, colors):
        if self.program_widget.image_widget.imageOrigin is None:
            return

        text = "Save region " if is_selected else "Save image "
        text += str(colors)
        filters = "PNG (*.png);; JPEG (*.jpg *.jpeg)"
        fname = QFileDialog.getSaveFileName(self, text, os.getcwd(), filters)[0]

        if not fname:
            self.status("Name empty!")
            return

        img = self.program_widget.image_widget.get_image(is_selected, colors)

        img.save(fname)
        self.status("Ready")

    def _menubar_data(self):
        return [
            ('&File', [
                ('&Open', self._open),
                ("", Separator()),
                ('Save to', [
                    ('RGB', self._save_generator(False, "RGB")),
                    ('HSV', self._save_generator(False, "HSV"))
                ]),
                ("Save region to", [
                    ("RGB", self._save_generator(True, "RGB")),
                    ("HSV", self._save_generator(True, "HSV"))
                ]),
                ("", Separator()),
                ('&Exit', {'triggered': qApp.quit, 'shortcut': 'Ctrl+Q', 'icon': None}),
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
            elif isinstance(info, list):
                submenu = QMenu(name, self)
                menu.addMenu(submenu)
                self._generate_submenu(submenu, info)
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

        self.image_widget = ImageWidget(parent)
        self.hist_widget = HistogramWidget(parent)
        self.coord_label = QLabel("", self)
        self.pixel_rgb_label = QLabel('', self)
        self.pixel_hsv_label = QLabel('', self)
        self.pixel_lab_label = QLabel('', self)

        h_slider_box, self.h_slider = self._get_slider_box(
            "H:", -180, 180, 60, self.slider_update
        )

        s_slider_box, self.s_slider = self._get_slider_box(
            "S:", -100, 100, 10, self.slider_update
        )

        v_slider_box, self.v_slider = self._get_slider_box(
            "V:", -100, 100, 10, self.slider_update
        )

        self._set_default()

        self.image_widget.selection_update.connect(self.selection_upd)

        hbox = QHBoxLayout()
        hbox.addWidget(self.image_widget, 20)

        vbox = QVBoxLayout()
        vbox.addWidget(self.hist_widget)
        vbox.addWidget(self.coord_label)
        vbox.addWidget(self.pixel_rgb_label)
        vbox.addWidget(self.pixel_hsv_label)
        vbox.addWidget(self.pixel_lab_label)

        vbox.addLayout(h_slider_box)
        vbox.addLayout(s_slider_box)
        vbox.addLayout(v_slider_box)

        hbox.addLayout(vbox, 1)

        self.setLayout(hbox)

    def _get_slider_box(self, label_name, _min, _max, _interval, callback, layout=Qt.Horizontal) -> Tuple[QBoxLayout, QSlider]:
        slider = QSlider(layout, self)
        slider.setMinimum(_min)
        slider.setMaximum(_max)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setTickInterval(_interval)

        slider.sliderReleased.connect(callback)

        box = QHBoxLayout()
        box.addWidget(QLabel(label_name, self))
        box.addWidget(slider)

        return box, slider

    def _set_default(self):
        self.coord_label.setText("Select pixel")
        self.pixel_rgb_label.setText("Select pixel")
        self.pixel_hsv_label.setText("Select pixel")
        self.pixel_lab_label.setText("Select pixel")

        self.h_slider.setValue(0)

    def slider_update(self):
        self.image_widget.shift_hsv = self.h_slider.value(), self.s_slider.value(), self.v_slider.value()

    def selection_upd(self):
        img = self.image_widget.selected(self.hist_widget.speed)
        print(img.width(), img.height())

        coord = self.image_widget.selection_img
        self.coord_label.setText("{}, {} x {}, {}".format(
            coord.left(), coord.top(),
            coord.right(), coord.bottom()
        ))

        if 1 == img.width() == img.height():
            pixel = QColor(img.pixel(0, 0))

            self.pixel_rgb_label.setText(
                "R:{}, G:{}, B:{}".format(pixel.red(), pixel.green(), pixel.blue())
            )

            self.pixel_hsv_label.setText(
                "H:{}, S:{}, V:{}".format(pixel.hue(), pixel.saturation(), pixel.value())
            )

            self.pixel_lab_label.setText(
                "L:{:.1f}, A:{:.1f}, B:{:.1f}".format(*pixel.lab())
            )
        else:
            self.pixel_rgb_label.setText("Select one pixel")
            self.pixel_hsv_label.setText("Select one pixel")
            self.pixel_lab_label.setText("Select one pixel")

        self.hist_widget.calc_image(img)

    def set_image(self, image: QImage):
        self.image_widget.set_image(image)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    prg = Program(640, 480)
    sys.exit(app.exec_())
