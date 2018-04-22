import numpy as np
from numpy import ndarray
from PyQt5 import QtGui
from PyQt5.QtGui import QImage

from utils import QColor, hsv_ranged, inrange
from qimage2ndarray import array2qimage


def _rgb_to_hsv(rgb: np.ndarray) -> np.ndarray:
    input_shape = rgb.shape
    rgb = rgb.reshape(-1, 4)
    r, g, b, a = rgb[:, 0], rgb[:, 1], rgb[:, 2], rgb[:, 3]

    maxc = np.maximum(np.maximum(r, g), b)
    minc = np.minimum(np.minimum(r, g), b)
    v = maxc

    deltac = maxc - minc
    s = deltac / maxc
    deltac[deltac == 0] = 1  # to not divide by zero (those results in any way would be overridden in next lines)
    rc = (maxc - r) / deltac
    gc = (maxc - g) / deltac
    bc = (maxc - b) / deltac

    h = 4.0 + gc - rc
    h[g == maxc] = 2.0 + rc[g == maxc] - bc[g == maxc]
    h[r == maxc] = bc[r == maxc] - gc[r == maxc]
    h[minc == maxc] = 0.0

    h = (h / 6.0) % 1.0
    h *= 360
    s *= 100
    v = v * (100 / 255)

    res = np.dstack([h, s, v, a])
    return res.reshape(input_shape)


def _hsv_to_rgb(hsv: np.ndarray) -> np.ndarray:
    """
    >>> from colorsys import hsv_to_rgb as hsv_to_rgb_single
    >>> 'r={:.0f} g={:.0f} b={:.0f}'.format(*hsv_to_rgb_single(0.60, 0.79, 239))
    'r=50 g=126 b=239'
    >>> 'r={:.0f} g={:.0f} b={:.0f}'.format(*hsv_to_rgb_single(0.25, 0.35, 200.0))
    'r=165 g=200 b=130'
    >>> np.set_printoptions(0)
    >>> _hsv_to_rgb(np.array([[[0.60, 0.79, 239], [0.25, 0.35, 200.0]]]))
    array([[[  50.,  126.,  239.],
            [ 165.,  200.,  130.]]])
    >>> 'r={:.0f} g={:.0f} b={:.0f}'.format(*hsv_to_rgb_single(0.60, 0.0, 239))
    'r=239 g=239 b=239'
    >>> _hsv_to_rgb(np.array([[0.60, 0.79, 239], [0.60, 0.0, 239]]))
    array([[  50.,  126.,  239.],
           [ 239.,  239.,  239.]])
    """
    input_shape = hsv.shape
    hsv = hsv.reshape(-1, 4)
    h, s, v, a = hsv[:, 0], hsv[:, 1], hsv[:, 2], hsv[:, 3]

    i = np.int32((h / 60) % 6)
    _t = (h % 60.) / 60.

    v_min = v * (100. - s) / 100.
    # add = (v - v_min) * (h % 60) / 60.
    # add = v * s / 100 * _t
    v_inc = v * (1 - s * (1 - _t) * 0.01)  # v_min + add
    v_dec = v * (1 - s * _t * 0.01)
    i = i % 6

    a: np.ndarray = a

    rgb = np.zeros_like(hsv)
    v, v_inc, v_min, v_dec, a = v.reshape(-1, 1), v_inc.reshape(-1, 1), v_min.reshape(-1, 1), v_dec.reshape(-1, 1), a.reshape(-1, 1)
    rgb[i == 0] = np.hstack([v, v_inc, v_min, a])[i == 0]
    rgb[i == 1] = np.hstack([v_dec, v, v_min, a])[i == 1]
    rgb[i == 2] = np.hstack([v_min, v, v_inc, a])[i == 2]
    rgb[i == 3] = np.hstack([v_min, v_dec, v, a])[i == 3]
    rgb[i == 4] = np.hstack([v_inc, v_min, v, a])[i == 4]
    rgb[i == 5] = np.hstack([v, v_min, v_dec, a])[i == 5]
    rgb[s == 0.0] = np.hstack([v, v, v, a])[s == 0.0]

    rgb *= 2.55

    return rgb.reshape(input_shape)


def getdata(image):
    # PyQt4/PyQt5's QImage.bits() returns a sip.voidptr that supports
    # conversion to string via asstring(size) or getting its base
    # address via int(...):
    return (int(image.bits()), False)


def qimageview(image: QImage) -> ndarray:
    if not isinstance(image, QtGui.QImage):
        raise TypeError("image argument must be a QImage instance")

    shape = image.height(), image.width(), 4
    strides0 = image.bytesPerLine()

    format = image.format()

    dtype = "|u1"
    strides1 = 4
    strides2 = 1

    if format == QtGui.QImage.Format_Invalid:
        raise ValueError("qimageview got invalid QImage")

    image.__array_interface__ = {
        'shape': shape,
        'typestr': dtype,
        'data': getdata(image),
        'strides': (strides0, strides1, strides2),
        'version': 3,
    }

    result = np.asarray(image)
    result[..., :3] = result[..., 2::-1]
    del image.__array_interface__
    return result


def shift_hsv(image: QImage, dh, ds, dv):
    yield 0.0
    rgb = qimageview(image.copy())
    yield 0.18
    hsv = _rgb_to_hsv(rgb)
    yield 0.36
    hsv[..., 0] += dh
    hsv[..., 0] %= 360
    yield 0.54
    hsv[..., 1] += ds
    np.clip(hsv[..., 1], 0, 100, out=hsv[..., 1])
    yield 0.72
    hsv[..., 2] += dv
    np.clip(hsv[..., 2], 0, 100, out=hsv[..., 2])
    yield 0.9

    new_img = _hsv_to_rgb(hsv)
    yield 1
    img: QImage = array2qimage(new_img)
    yield img


def shift_old_hsv(image: QImage, dh, ds, dv):
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
