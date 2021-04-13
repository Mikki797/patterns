from PyQt5 import QtWidgets
# from MainWindow import MainWindow
from LoginWindow import LoginWindow
import sys

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = LoginWindow()

    win.show()
    sys.exit(app.exec())