import numpy as np
from numpy import ndarray
from PyQt5 import QtGui
from PyQt5.QtGui import QImage

from utils import QColor, hsv_ranged, inrange
from qimage2ndarray import array2qimage
from qimage2ndarray.qimageview_python import qimageview as _qimageview


def _rgb_to_hsv(rgb: np.ndarray) -> np.ndarray:
    """
    >>> from colorsys import rgb_to_hsv as rgb_to_hsv_single
    >>> 'h={:.2f} s={:.2f} v={:.2f}'.format(*rgb_to_hsv_single(50, 120, 239))
    'h=0.60 s=0.79 v=239.00'
    >>> 'h={:.2f} s={:.2f} v={:.2f}'.format(*rgb_to_hsv_single(163, 200, 130))
    'h=0.25 s=0.35 v=200.00'
    >>> np.set_printoptions(2)
    >>> rgb_to_hsv(np.array([[[50, 120, 239], [163, 200, 130]]]))
    array([[[   0.6 ,    0.79,  239.  ],
            [   0.25,    0.35,  200.  ]]])
    >>> 'h={:.2f} s={:.2f} v={:.2f}'.format(*rgb_to_hsv_single(100, 100, 100))
    'h=0.00 s=0.00 v=100.00'
    >>> rgb_to_hsv(np.array([[50, 120, 239], [100, 100, 100]]))
    array([[   0.6 ,    0.79,  239.  ],
           [   0.  ,    0.  ,  100.  ]])
    """
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

    i = np.int32(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6

    a: np.ndarray = a

    rgb = np.zeros_like(hsv)
    v, t, p, q, a = v.reshape(-1, 1), t.reshape(-1, 1), p.reshape(-1, 1), q.reshape(-1, 1), a.reshape(-1, 1)
    print(a.shape, v.shape)
    rgb[i == 0] = np.hstack([v, t, p, a])[i == 0]
    rgb[i == 1] = np.hstack([q, v, p, a])[i == 1]
    rgb[i == 2] = np.hstack([p, v, t, a])[i == 2]
    rgb[i == 3] = np.hstack([p, q, v, a])[i == 3]
    rgb[i == 4] = np.hstack([t, p, v, a])[i == 4]
    rgb[i == 5] = np.hstack([v, p, q, a])[i == 5]
    rgb[s == 0.0] = np.hstack([v, v, v, a])[s == 0.0]

    return rgb.reshape(input_shape)


def getdata(image):
    # PyQt4/PyQt5's QImage.bits() returns a sip.voidptr that supports
    # conversion to string via asstring(size) or getting its base
    # address via int(...):
    return (int(image.bits()), False)


def qimageview(image):
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
    rgb = qimageview(image)
    yield 0.18
    hsv = _rgb_to_hsv(rgb)
    yield 0.36
    hsv[..., 0] += dh / 360
    hsv[..., 0] %= 1.0
    yield 0.54
    hsv[..., 1] = np.ones_like(hsv[..., 1])
    # hsv[..., 1] += ds / 255
    # np.clip(hsv[..., 1], 0, 1, out=hsv[..., 1])
    yield 0.72
    hsv[..., 2] += dv
    np.clip(hsv[..., 2], 0, 255, out=hsv[..., 2])
    yield 0.9
    hsv[..., 1] %= 1.0

    new_img = _hsv_to_rgb(hsv)
    # new_img = rgb
    yield 1
    # new_img[..., 2], new_img[..., 0] = new_img[..., 0], new_img[..., 2]
    # new_img[..., 0], new_img[..., 2] = new_img[..., 0], new_img[..., 2]
    img: QImage = array2qimage(new_img)
    img = img.convertToFormat(QImage.Format_RGBA8888)
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
