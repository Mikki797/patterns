from PyQt5 import QtWidgets
from MainWindow import MainWindow
import sys

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = MainWindow()

    win.show()
    sys.exit(app.exec())