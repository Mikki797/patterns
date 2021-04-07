from PyQt5.QtWidgets import QMainWindow, QAction, QTableWidgetItem, QPushButton, QHBoxLayout, QWidget
from PyQt5.QtCore import Qt, QVariant
from mainform import Ui_MainWindow

from decimal import Decimal

from database import Database
from builder import OrderBuilder

TITLE = 'Лабораторная №5'


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.centralwidget.setLayout(self.ui.horizontalLayout)
        self.setWindowTitle(TITLE)

        self.add_menu()

        self.db = Database
        self.db.create_db()

        self.products = {a[0]: Decimal(a[1]) for a in self.db.get_products()}
        self.create_product_list()

        self.boxes_names = ['Коробка']

        self.order_builder = OrderBuilder(self.ui.treeWidget, 'Коробка', self.products['Коробка'])
        for col in range(not self.ui.treeWidget.columnCount()):
            self.ui.treeWidget.resizeColumnToContents(col)

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
        def create_widget_with_buttons(product):
            def create_button(text, color):
                btn = QPushButton(text)
                size = 20
                btn.setFixedSize(size, size)
                btn.setStyleSheet(f'QPushButton {{color: {color}}}')
                btn.clicked.connect(self.item_clicked)
                btn.setProperty("product", QVariant(product))
                return btn

            btn_plus = create_button('+', 'green')
            btn_minus = create_button('-', 'red')

            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.addWidget(btn_plus)
            layout.addWidget(btn_minus)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)

            widget.setLayout(layout)
            return widget

        def create_item(text: str) -> QTableWidgetItem:
            item = QTableWidgetItem(str(text))
            item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            return item

        products = self.products

        row_count = len(products)
        col_count = 3
        self.ui.tableWidget.setRowCount(row_count)
        self.ui.tableWidget.setColumnCount(col_count)
        for row, (product_name, product_price) in enumerate(products.items()):
            self.ui.tableWidget.setItem(row, 0, create_item(product_name))
            self.ui.tableWidget.setItem(row, 1, create_item(product_price))
            self.ui.tableWidget.setCellWidget(row, col_count-1, create_widget_with_buttons(product_name))

        self.ui.tableWidget.resizeColumnsToContents()
        self.ui.tableWidget.setHorizontalHeaderItem(col_count-1, QTableWidgetItem())

    def item_clicked(self):
        btn = self.sender()
        product = btn.property("product")

        current_item = self.ui.treeWidget.currentItem()
        if current_item is not None and current_item.name in self.boxes_names:
            self.order_builder.set_current_box(current_item)
            if product in self.boxes_names:
                self.order_builder.add_box(product, self.products[product])
            else:
                self.order_builder.add_product(product, self.products[product], 1)
            self.order_builder.current_box().setExpanded(True)




