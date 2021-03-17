from PyQt5.QtWidgets import QMainWindow, QAction
from mainform import Ui_MainWindow

from database import Database

TITLE = 'Лабораторная №5'


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # self.ui.centralwidget.setLayout(self.ui.main_layout)
        self.setWindowTitle(TITLE)

        self.add_menu()

        db = Database
        db.create_db()

    def add_menu(self):
        self.add_about_menu()

    def add_about_menu(self):
        about_menu = self.ui.menubar.addMenu(self.tr("&Помощь"))

        about_author_action = QAction("О авторе", self)
        about_author_action.triggered.connect(self.about_author)
        about_menu.addAction(about_author_action)

    def about_author(self):
        self.message("Об авторе", "Козловский А.М. Группа М8О-412Б-17")