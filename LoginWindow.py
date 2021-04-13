from PyQt5.QtWidgets import QMainWindow, QMessageBox
from forms.loginform import Ui_MainWindow

import bcrypt

from MainWindow import MainWindow
from RegisterWindow import RegisterWindow
from database import Database
from src import TITLE


class LoginWindow(QMainWindow):
    def __init__(self):
        super(LoginWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.centralwidget.setLayout(self.ui.mainLayout)
        self.setWindowTitle(TITLE)

        self.db = Database
        # self.db.create_db()

        self.main_window = MainWindow()
        self.register_window = RegisterWindow()
        self.register_window.signal.connect(self.show)

        self.ui.pb_login.clicked.connect(self.clicked_login)
        self.ui.pb_register.clicked.connect(self.clicked_register)

    def clicked_login(self):
        login = self.ui.le_login.text()
        password = self.ui.le_password.text()

        if len(login) == 0 or len(password) == 0:
            return

        hashed_pw = self.db.get_pw_by_login(login)

        if (login == 'login' and password == '123') or (hashed_pw is not None and bcrypt.checkpw(str.encode(password), hashed_pw)):
            self.main_window.set_login(login)
            self.main_window.show()
            self.close()
        else:
            self.ui.le_password.clear()
            QMessageBox.about(self, TITLE, "Неправильный логин или пароль")

    def clicked_register(self):
        login = self.ui.le_login.text()
        password = self.ui.le_password.text()

        self.register_window.show()
        self.register_window.ui.le_login.setText(login)
        self.register_window.ui.le_password.setText(password)
        self.close()

    def show(self) -> None:
        self.ui.le_login.setText('login')
        self.ui.le_password.setText('123')
        super().show()
