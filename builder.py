from PyQt5.QtWidgets import QTreeWidget

from decimal import Decimal
from factory import ProductFactory, BoxFactory, AbstractWidget
from collections.abc import Iterable
from typing import Tuple


class OrderBuilder(Iterable):
    def __init__(self, tree_widget: QTreeWidget, box_name: str, box_price: Decimal):
        self.tree_widget = tree_widget
        self.tree_widget.clear()
        self.product_factory = ProductFactory()
        self.box_factory = BoxFactory()
        self._current_box = self.box_factory.create_component(box_name, 1, box_price, 0)
        self._current_box_widget = self.box_factory.create_widget(tree_widget, self._current_box)

    def set_current_box_widget(self, box_widget: AbstractWidget):
        self._current_box_widget = box_widget
        self._current_box = self._current_box_widget.component

    def current_box_widget(self):
        return self._current_box_widget

    def add_product(self, name: str, price: Decimal, number: int) -> None:
        if number == 0:
            return

        for i in range(self._current_box_widget.childCount()):
            item_child = self._current_box_widget.child(i)
            if item_child.name == name:
                if (item_child.number + number) <= 0:
                    self._current_box.remove(item_child.component)
                    self._current_box_widget.removeChild(item_child)
                else:
                    item_child.number += number
                    # item_child.component.number += number
                    item_child.price = item_child.number * item_child.price
                return

        if number > 0:
            product = self.product_factory.create_component(name, number, price, self._current_box.depth)
            self.product_factory.create_widget(self._current_box_widget, product)
            self._current_box.add(product)

    def add_box(self, name: str, price: Decimal) -> None:
        box = self.box_factory.create_component(name, 1, price, self._current_box.depth+1)
        self.box_factory.create_widget(self._current_box_widget, box)
        self._current_box.add(box)

    def substract_product(self, name: str, price: Decimal, number: int) -> None:
        self.add_product(name, price, -number)

    def set_number(self, widget: AbstractWidget, value: int) -> None:
        if value == 0:
            widget.parent().component.remove(widget.component)
            widget.parent().removeChild(widget)
        else:
            widget.component.number = value
            widget.price = widget.number * widget.component.price

    def get_dict(self) -> Tuple:
        name = self.tree_widget.topLevelItem(0).component.name
        return name, self.tree_widget.topLevelItem(0).component.get_dict()

    def __iter__(self):
        return iter(self.tree_widget.topLevelItem(0).component)

