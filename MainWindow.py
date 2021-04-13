from PyQt5.QtWidgets import QMainWindow, QAction, QTableWidgetItem, QPushButton, QHBoxLayout, QWidget, QMessageBox
from PyQt5.QtCore import Qt, QVariant
from PyQt5.QtGui import QCloseEvent
from forms.mainform import Ui_MainWindow

from decimal import Decimal
from datetime import datetime

from database import Database, OrderStatus, DeliveryType
from builder import OrderBuilder
from src import TITLE

PRODUCTS_DISCOUNT = 0.95
DELIVERY_DISCOUNT = 0.9


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.centralwidget.setLayout(self.ui.mainLayout)
        self.setWindowTitle(TITLE)

        self.login = None

        self.add_menu()

        self.db = Database
        self.products = {a[0]: Decimal(a[1]) for a in self.db.get_products()}
        self.create_product_list()

        self.boxes_names = ['Коробка']

        self.order_builder = OrderBuilder(self.ui.treeWidget, 'Коробка', self.products['Коробка'])
        for col in range(not self.ui.treeWidget.columnCount()):
            self.ui.treeWidget.resizeColumnToContents(col)

        self.ui.pb_save.clicked.connect(self.save_order)
        self.ui.pb_order.clicked.connect(self.make_order)

        self.ui.cb_delivery.currentIndexChanged[int].connect(self.delivery_changed)

        self.ui.sb_sum.valueChanged[float].connect(self.total_changed)
        self.ui.sb_delivery.valueChanged[float].connect(self.total_changed)

        self.ui.cb_discount.stateChanged[int].connect(self.discount_changed)
        if datetime.weekday(datetime.now()) in [5, 6]:
            self.ui.cb_discount.setChecked(Qt.CheckState.Checked)
            self.is_discount = True
        else:
            self.is_discount = False

        self.set_sum()

    def add_menu(self):
        self.add_order_menu()
        self.add_about_menu()

    def add_order_menu(self):
        order_menu = self.ui.menubar.addMenu(self.tr("&Заказ"))

        clear_order_action = QAction("Очистить", self)
        clear_order_action.triggered.connect(self.clear_order)
        order_menu.addAction(clear_order_action)

    def add_about_menu(self):
        about_menu = self.ui.menubar.addMenu(self.tr("&Помощь"))

        about_author_action = QAction("Об авторе", self)
        about_author_action.triggered.connect(self.about_author)
        about_menu.addAction(about_author_action)

    def about_author(self):
        QMessageBox.about(self, "Об авторе", "Козловский А.М. Группа М8О-412Б-17")
        # msg_box.exec()

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
        add = True if btn.text() == '+' else False
        product_name = btn.property("product")

        current_item = self.ui.treeWidget.currentItem()
        if current_item is not None and current_item.name in self.boxes_names:
            self.order_builder.set_current_box_widget(current_item)
            if product_name in self.boxes_names:
                self.order_builder.add_box(product_name, self.products[product_name])
            else:
                if add:
                    self.order_builder.add_product(product_name, self.products[product_name], 1)
                else:
                    self.order_builder.substract_product(product_name, self.products[product_name], 1)
            self.order_builder.current_box_widget().setExpanded(True)

        self.set_sum()

    def product_value_change_number(self, value: int) -> None:
        tree_widget = self.sender().parent().parent().parent()
        product_widget = tree_widget.itemAt(self.sender().parent().pos())
        self.order_builder.set_number(product_widget, value)
        self.set_sum()

    def delivery_changed(self, index: int):
        koef = Decimal(DELIVERY_DISCOUNT if self.is_discount else 1)
        if index == 0:
            self.ui.sb_delivery.setValue(koef*0)
        elif index == 1:
            self.ui.sb_delivery.setValue(koef*100)
        elif index == 2:
            self.ui.sb_delivery.setValue(koef*200)

    def set_sum(self):
        koef = Decimal(PRODUCTS_DISCOUNT if self.is_discount else 1)
        self.ui.sb_sum.setValue(koef*sum(product.number * product.price for product in self.order_builder))

    def discount_changed(self, state: int):
        self.is_discount = True if state == Qt.CheckState.Checked else False
        self.set_sum()

    def total_changed(self, value: float):
        self.ui.sb_total.setValue(self.ui.sb_sum.value() + self.ui.sb_delivery.value())

    def save_order(self):
        try:
            self.db.delete_save_order(self.login)
            self.add_order(OrderStatus.SAVE)
        except Exception as e:
            QMessageBox.about(self, TITLE, e.args[0])
        else:
            QMessageBox.about(self, TITLE, "Заказ успешно сохранен!")

    def make_order(self):
        try:
            self.db.delete_save_order(self.login)
            self.add_order(OrderStatus.IN_WAY)
        except Exception as e:
            QMessageBox.about(self, TITLE, e.args[0])
        else:
            QMessageBox.about(self, TITLE, "Заказ успешно сделан!")
        self.clear_order()

    def add_order(self, order_status: OrderStatus):
        delivery_type = None
        if self.ui.cb_delivery.currentText() == "Нет":
            delivery_type = DeliveryType.NO_DELIVERY
        elif self.ui.cb_delivery.currentText() == "Обычная":
            delivery_type = DeliveryType.COMMON
        elif self.ui.cb_delivery.currentText() == "Срочная":
            delivery_type = DeliveryType.EXPRESS
        self.db.add_order(self.login, order_status, delivery_type, self.ui.cb_discount.isChecked(),
                          self.ui.sb_total.value(), self.order_builder.get_dict())

    def closeEvent(self, event: QCloseEvent) -> None:
        pass
        # TODO раскоментить
        # reply = QMessageBox.question(self, TITLE, "Сохранить заказ?",
        #                              QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No |
        #                              QMessageBox.StandardButton.Cancel)
        # if reply == QMessageBox.StandardButton.Yes:
        #     self.save_order()
        # elif reply == QMessageBox.StandardButton.No:
        #     self.close()
        # else:
        #     event.ignore()

    def set_login(self, login):
        self.login = login

    def clear_order(self):
        self.order_builder = OrderBuilder(self.ui.treeWidget, 'Коробка', self.products['Коробка'])
        self.ui.cb_delivery.setCurrentIndex(0)
        self.set_sum()
