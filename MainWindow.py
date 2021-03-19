from PyQt5.QtWidgets import QMainWindow, QAction, QTableWidgetItem, QPushButton, QHBoxLayout, QWidget
from PyQt5.QtCore import Qt, QVariant
from mainform import Ui_MainWindow

from collections import namedtuple

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

        self.db = Database
        self.db.create_db()

        self.products = None
        self.create_product_list()

        self.ui.tableWidget.cellClicked[int, int].connect(self.item_clicked)

    def add_menu(self):
        self.add_about_menu()

    def add_about_menu(self):
        about_menu = self.ui.menubar.addMenu(self.tr("&Помощь"))

        about_author_action = QAction("О авторе", self)
        about_author_action.triggered.connect(self.about_author)
        about_menu.addAction(about_author_action)

    def about_author(self):
        self.message("Об авторе", "Козловский А.М. Группа М8О-412Б-17")

    def create_product_list(self):
        def create_widget_with_buttons(row):
            btn_plus = QPushButton('+')
            size = 20
            btn_plus.setFixedSize(size, size)
            btn_plus.setStyleSheet('QPushButton {color: green}')
            btn_plus.clicked.connect(self.item_clicked)
            btn_plus.setProperty("row", QVariant(row))

            btn_minus = QPushButton('-')
            btn_minus.setFixedSize(size, size)
            btn_minus.setStyleSheet('QPushButton {color: red}')
            btn_minus.clicked.connect(self.item_clicked)

            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.addWidget(btn_plus)
            layout.addWidget(btn_minus)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)

            widget.setLayout(layout)
            return widget

        Product = namedtuple('Product', ['name', 'price'])
        products = list(map(Product._make, self.db.get_products()))
        self.products = products

        row_count = len(products)
        col_count = len(products[0])+1
        self.ui.tableWidget.setRowCount(row_count)
        self.ui.tableWidget.setColumnCount(col_count)
        for row, product in enumerate(products):
            self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(product.name))
            self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(product.price))

            self.ui.tableWidget.setCellWidget(row, col_count-1, create_widget_with_buttons(row))

        self.ui.tableWidget.resizeColumnsToContents()
        self.ui.tableWidget.setHorizontalHeaderItem(col_count-1, QTableWidgetItem())
        # self.ui.tableWidget.

    def item_clicked(self):
        btn = self.sender()
        row = btn.property("row")
        print(row)


