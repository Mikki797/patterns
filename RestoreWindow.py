from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import pyqtSignal, QRegExp
from forms.restoreform import Ui_MainWindow

import bcrypt

from database import Database, User
from src import TITLE


class RestoreWindow(QMainWindow):
    signal = pyqtSignal()

    def __init__(self):
        super(RestoreWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.centralwidget.setLayout(self.ui.mainLayout)
        self.setWindowTitle(TITLE)

        self.db = Database
        self.login = None
        self.secret_question = None
        self.hashed_secret_answer = None

        self.ui.pb_restore.clicked.connect(self.clicked_restore)
        self.ui.pb_cancel.clicked.connect(self.clicked_cancel)

    def clicked_restore(self):
        if not self.ui.le_secret_answer.text() or not self.ui.le_password.text() or \
                not self.ui.le_password_again.text():
            QMessageBox.about(self, TITLE, "Не все строки заполнены")
            return

        if self.ui.le_password.text() != self.ui.le_password_again.text():
            QMessageBox.about(self, TITLE, "Пароли не совпадают")
            return

        if self.hashed_secret_answer is not None and \
                bcrypt.checkpw(str.encode(self.ui.le_secret_answer.text()), self.hashed_secret_answer):
            hash_pw = bcrypt.hashpw(str.encode(self.ui.le_password.text()), bcrypt.gensalt())
            self.db.set_new_password(self.ui.le_login.text(), hash_pw)

            QMessageBox.about(self, TITLE, "Новый пароль успешно установлен")
            self.close()
            self.signal.emit()
        else:
            self.ui.le_password.clear()
            self.ui.le_password_again.clear()
            QMessageBox.about(self, TITLE, "Неправильный логин или пароль")

    def clicked_cancel(self):
        self.close()
        self.signal.emit()

    def set_params(self, login: str, secret_question: str, secret_answer: bytes) -> None:
        self.login = login
        self.secret_question = secret_question
        self.hashed_secret_answer = secret_answer

    def show(self) -> None:
        self.ui.le_login.setText(self.login)
        self.ui.le_secret_question.setText(self.secret_question)
        self.ui.le_secret_answer.clear()
        self.ui.le_password.clear()
        self.ui.le_password_again.clear()
        super().show()
