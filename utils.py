from PyQt5.QtGui import QColor as _QColor


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
