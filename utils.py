from PyQt5.QtGui import QColor as _QColor


def inrange(value, _min, _max):
    if value > _max:
        return _max
    if _min > value:
        return _min
    return value
    # return max(min(value, _max), _min)


def hsv_ranged(h, s, v):
    return (
        (h + 360 * 2) % 360,
        inrange(s, 0, 255),
        inrange(v, 0, 255)
    )


class QColor(_QColor):
    def __add__(self, other: "QColor"):
        return QColor(
            self.red() + other.red(),
            self.green() + other.green(),
            self.blue() + other.blue()
        )

    def __str__(self):
        if self.spec() == self.Rgb:
            return "<QColor {}, {}, {}>".format(
                self.green(),
                self.red(),
                self.blue()
            )

        return super().__str__()

    def lab(self):
        num = 0
        rgb = [0, 0, 0]

        input_color = self.red(), self.green(), self.blue()

        for value in input_color:
            value = float(value) / 255

            if value > 0.04045:
                value = ((value + 0.055) / 1.055) ** 2.4
            else:
                value = value / 12.92

            rgb[num] = value * 100
            num = num + 1

        xyz = [0, 0, 0, ]

        x = rgb[0] * 0.4124 + rgb[1] * 0.3576 + rgb[2] * 0.1805
        y = rgb[0] * 0.2126 + rgb[1] * 0.7152 + rgb[2] * 0.0722
        z = rgb[0] * 0.0193 + rgb[1] * 0.1192 + rgb[2] * 0.9505
        xyz[0] = round(x, 4)
        xyz[1] = round(y, 4)
        xyz[2] = round(z, 4)

        xyz[0] = float(xyz[0]) / 95.047  # ref_X =  95.047   Observer= 2°, Illuminant= D65
        xyz[1] = float(xyz[1]) / 100.0  # ref_Y = 100.000
        xyz[2] = float(xyz[2]) / 108.883  # ref_Z = 108.883

        num = 0
        for value in xyz:

            if value > 0.008856:
                value = value ** (0.3333333333333333)
            else:
                value = (7.787 * value) + (16 / 116)

            xyz[num] = value
            num = num + 1

        lab = [0, 0, 0]

        L = (116 * xyz[1]) - 16
        a = 500 * (xyz[0] - xyz[1])
        b = 200 * (xyz[1] - xyz[2])

        lab[0] = round(L, 4)
        lab[1] = round(a, 4)
        lab[2] = round(b, 4)

        return lab
