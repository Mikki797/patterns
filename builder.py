from composite import Product, Box
from PyQt5.QtWidgets import QTreeWidget

from decimal import Decimal


class OrderBuilder:
    def __init__(self, tree_widget: QTreeWidget, box_name: str, box_price: Decimal):
        self.tree_widget = tree_widget
        self._current_box = Box(box_name, box_price)
        tree_widget.addTopLevelItem(self._current_box)

    def set_current_box(self, box):
        self._current_box = box

    def current_box(self):
        return self._current_box

    def add_product(self, name: str, price: Decimal, number: int) -> None:
        product = Product(name, price, number)
        self._current_box.add(product)

    def add_box(self, name: str, price: Decimal) -> None:
        box = Box(name, price)
        self._current_box.add(box)


