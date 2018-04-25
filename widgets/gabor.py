import numpy as np
from qimage2ndarray import array2qimage
from scipy.signal import convolve2d

from .processing import qimageview


def _sigma_prefactor(bandwidth):
    b = bandwidth
    # See http://www.cs.rug.nl/~imaging/simplecell.html
    return 1.0 / np.pi * np.sqrt(np.log(2) / 2.0) * \
        (2.0 ** b + 1) / (2.0 ** b - 1)


def gabor_kernel(frequency, theta=0, bandwidth=1, sigma_x=None, sigma_y=None,
                 n_stds=3, offset=0):
    if sigma_x is None:
        sigma_x = _sigma_prefactor(bandwidth) / frequency
    if sigma_y is None:
        sigma_y = _sigma_prefactor(bandwidth) / frequency

    x0 = np.ceil(max(np.abs(n_stds * sigma_x * np.cos(theta)),
                     np.abs(n_stds * sigma_y * np.sin(theta)), 1))
    y0 = np.ceil(max(np.abs(n_stds * sigma_y * np.cos(theta)),
                     np.abs(n_stds * sigma_x * np.sin(theta)), 1))
    y, x = np.mgrid[-y0:y0 + 1, -x0:x0 + 1]

    rotx = x * np.cos(theta) + y * np.sin(theta)
    roty = -x * np.sin(theta) + y * np.cos(theta)

    g = np.zeros(y.shape, dtype=np.complex)
    g[:] = np.exp(-0.5 * (rotx ** 2 / sigma_x ** 2 + roty ** 2 / sigma_y ** 2))
    g /= 2 * np.pi * sigma_x * sigma_y
    g *= np.exp(1j * (2 * np.pi * frequency * rotx + offset))

    return g


def _gabor(image, frequency, theta=0, bandwidth=1, sigma_x=None,
          sigma_y=None, n_stds=3, offset=0, mode='reflect', cval=0):
    g = gabor_kernel(frequency, theta, bandwidth, sigma_x, sigma_y, n_stds,
                     offset)

    filtered_real = convolve2d(image, np.real(g), mode=mode)
    filtered_imag = convolve2d(image, np.imag(g), mode=mode)

    return filtered_real, filtered_imag


def gabor(image, theta):
    rgb = qimageview(image.copy())

    real = np.zeros_like(rgb)
    imag = np.zeros_like(rgb)

    real[..., 0], imag[..., 0] = _gabor(rgb[..., 0], 1, theta=theta, mode="same")
    real[..., 1], imag[..., 1] = _gabor(rgb[..., 1], 1, theta=theta, mode="same")
    real[..., 2], imag[..., 2] = _gabor(rgb[..., 2], 1, theta=theta, mode="same")

    dist = (real ** 2 + imag ** 2)
    dist[..., 3] = rgb[..., 3]
    return array2qimage(dist)
