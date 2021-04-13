from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import pyqtSignal, QRegExp
from PyQt5.QtGui import QRegExpValidator
from forms.registerform import Ui_MainWindow

from psycopg2 import errors
import bcrypt

from database import Database, User
from src import TITLE


class RegisterWindow(QMainWindow):
    signal = pyqtSignal()

    def __init__(self):
        super(RegisterWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.centralwidget.setLayout(self.ui.mainLayout)
        self.setWindowTitle(TITLE)

        self.db = Database

        regex = QRegExp('[а-яА-Яa-zA-Z_]+')
        self.ui.le_name.setValidator(QRegExpValidator(regex))

        self.line_edits = (self.ui.le_login, self.ui.le_password, self.ui.le_password_again, self.ui.le_secret_question,
                           self.ui.le_secret_answer, self.ui.le_name)

        self.ui.pb_register.clicked.connect(self.clicked_register)
        self.ui.pb_cancel.clicked.connect(self.clicked_cancel)

    def clicked_register(self):
        if any([len(le.text()) == 0 for le in self.line_edits]):
            QMessageBox.about(self, TITLE, "Не все строки заполнены")
            return

        if self.ui.le_password.text() != self.ui.le_password_again.text():
            QMessageBox.about(self, TITLE, "Пароли не совпадают")
            return

        hash_pw = bcrypt.hashpw(str.encode(self.ui.le_password.text()), bcrypt.gensalt())
        try:
            self.db.register_user(User(self.ui.le_login.text(), hash_pw, self.ui.le_secret_question.text(),
                                       self.ui.le_secret_answer.text(), self.ui.le_name.text()))
        except ValueError as e:
            QMessageBox.about(self, TITLE, e.args[0])
        else:
            QMessageBox.about(self, TITLE, "Аккаунт успешно зарегистрирован!")
            self.close()
            self.signal.emit()

    def clicked_cancel(self):
        self.close()
        self.signal.emit()

    def show(self) -> None:
        for le in self.line_edits:
            le.clear()
        super().show()
