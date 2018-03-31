from PyQt5.QtGui import QImage

from utils import QColor, hsv_ranged, inrange


def shift_hsv_old(image, dh, ds, dv):
    for x in range(image.width()):
        yield x
        for y in range(image.height()):
            color = image.pixelColor(x, y)
            h, s, v, a = color.getHsv()
            color.setHsv(*hsv_ranged(h + dh, s + ds, v + dv), a)
            image.setPixelColor(x, y, color)


def shift_hsv(image: QImage, dh, ds, dv):
    for x in range(image.width()):
        yield x
        for y in range(image.height()):
            color = image.pixelColor(x, y)
            h, s, v, a = color.getHsv()
            color.setHsv(
                (h + dh + 360 * 2) % 360,
                inrange(s + ds, 0, 255),
                inrange(v + dv, 0, 255)
            )
            image.setPixel(x, y, color.rgb())


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
