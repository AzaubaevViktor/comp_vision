from PyQt5.QtGui import QImage

from utils import QColor, hsv_ranged


def shift_hsv(image, dh, ds, dv):
    for x in range(image.width()):
        yield x
        for y in range(image.height()):
            color = image.pixelColor(x, y)
            h, s, v, a = color.getHsv()
            color.setHsv(*hsv_ranged(h + dh, s + ds, v + dv), a)
            image.setPixelColor(x, y, color)


def rgb_to_hsv(image: QImage):
    for x in range(image.width()):
        yield x
        for y in range(image.height()):
            color = image.pixelColor(x, y)
            h, s, v, a = color.getHsv()
            color.setRgb(
                int(h / 360 * 255),
                int(s),
                int(v)
            )
            image.setPixelColor(x, y, color)
