from abc import ABC, ABCMeta, abstractmethod
from typing import Dict, Tuple, List, Union
from decimal import Decimal
from collections.abc import Iterable, Iterator

from PyQt5.QtWidgets import QTreeWidgetItem, QPushButton, QWidget, QHBoxLayout, QTreeWidget, QSpinBox
from PyQt5.QtCore import Qt, QVariant
from composite import Component


class SingletonABC(ABCMeta):
    _instance = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instance:
            cls._instance[cls] = super(SingletonABC, cls).__call__(*args, **kwargs)
        return cls._instance[cls]


class AbstractComponent(ABC, Component):
    def __init__(self, name: str, number: int, price: Decimal):
        self.name = name
        self.number = number
        self.price = price
        self._children = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def number(self) -> int:
        return self._number

    @property
    def price(self) -> Decimal:
        return self._price

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @number.setter
    def number(self, number: int) -> None:
        self._number = number

    @price.setter
    def price(self, price: Decimal) -> None:
        self._price = price


class QABCMeta(ABCMeta, type(QWidget)):
    pass


class TcWidget(ABC, metaclass=QABCMeta):
    pass


class AbstractWidget(Component, QTreeWidgetItem):
    def __init__(self, parent: Union[QTreeWidget, QTreeWidgetItem], component: AbstractComponent):
        super(QTreeWidgetItem, self).__init__(parent)
        self.component = component

    @property
    def name(self) -> str:
        return self.text(0)

    @property
    def price(self) -> Decimal:
        return Decimal(self.text(2))

    @name.setter
    def name(self, name: str) -> None:
        self.setText(0, name)

    @price.setter
    def price(self, price):
        pass


class Product(AbstractComponent):
    def is_composite(self) -> bool:
        return False

    def add(self, component: Component) -> None:
        pass

    def remove(self, component: Component) -> None:
        pass


class BoxIterator(Iterator):
    def __init__(self, box):
        self._box = box
        self._position = -1
        self._child_box = None

    def __next__(self):
        if self._position == -1:
            self._position += 1
            return self._box

        try:
            value = self._box._children[self._position]
            if value.is_composite():
                if self._child_box is None:
                    self._child_box = BoxIterator(value)
                try:
                    return self._child_box.__next__()
                except StopIteration:
                    self._child_box = None
                    self._position += 1
                    value = self._box._children[self._position]
            self._position += 1
        except IndexError:
            raise StopIteration()

        return value


class Box(AbstractComponent, Iterable):
    def __init__(self, name: str, price: Decimal, depth: int) -> None:
        super().__init__(name, 1, price)
        self._depth = depth
        self._children: List[Component] = []

    @property
    def depth(self) -> int:
        return self._depth

    def add(self, component: Component) -> None:
        if not component.is_composite():
            for child in self._children:
                if child.name == component.name:
                    child.number += 1
                    return

        self._children.append(component)

    def remove(self, component: Component) -> None:
        self._children.remove(component)

    def is_composite(self) -> bool:
        return True

    def get_dict(self):
        chilren_names = []
        for child in self._children:
            if child.is_composite():
                chilren_names.append((child.name, child.get_dict()))
            else:
                chilren_names.append((child.name, child.number))
        return chilren_names

    def __iter__(self):
        return BoxIterator(self)


class ProductWidget(AbstractWidget):
    def __init__(self, parent: Union[QTreeWidget, QTreeWidgetItem], product: AbstractComponent):
        def create_widget():
            def create_spin_box():
                sb = QSpinBox()
                sb.setRange(0, 100)
                # sb.valueChanged.connect(self.emitDataChanged)
                return sb

            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.addWidget(create_spin_box())
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)

            widget.setLayout(layout)
            return widget

        super().__init__(parent, product)

        widget = create_widget()
        self.treeWidget().setItemWidget(self, 1, widget)
        self.spin_box = widget.children()[0].itemAt(0).widget()
        main_window = self.treeWidget().parent().parent()
        self.spin_box.valueChanged[int].connect(main_window.product_value_change_number)

        self.name = product.name
        self.number = product.number
        self.price = product.price

    @property
    def number(self) -> int:
        return self.spin_box.value()

    @property
    def price(self) -> Decimal:
        return Decimal(self.component.price)

    @number.setter
    def number(self, number: int) -> None:
        self.spin_box.setValue(number)

    @price.setter
    def price(self, price: Decimal) -> None:
        self.setText(2, str(price))

    def add(self, child: AbstractWidget) -> None:
        pass

    def remove(self, child: AbstractWidget) -> None:
        pass

    def is_composite(self) -> bool:
        return False


class BoxWidget(AbstractWidget):
    def __init__(self, parent: Union[QTreeWidget, QTreeWidgetItem], box: AbstractComponent):
        super().__init__(parent, box)

        self.name = box.name
        self.price = box.price

    @property
    def number(self) -> int:
        return 1

    @property
    def price(self) -> Decimal:
        return Decimal(self.text(2))

    @price.setter
    def price(self, price: Decimal) -> None:
        self.setText(2, str(price))

    def add(self, child: AbstractWidget) -> None:
        self.addChild(child)

    def remove(self, child: AbstractWidget) -> None:
        self.removeChild(child)

    def is_composite(self) -> bool:
        return False


class AbstractFactory(metaclass=SingletonABC):
    @abstractmethod
    def create_component(self, name: str, number: int, price: Decimal, depth: int) -> AbstractComponent:
        pass

    @abstractmethod
    def create_widget(self, parent: Union[QTreeWidget, QTreeWidgetItem], component: AbstractComponent) -> AbstractWidget:
        pass


class ProductFactory(AbstractFactory):
    _flyweights: Dict[Tuple, Product] = {}

    def create_component(self, name: str, number: int, price: Decimal, depth: int) -> AbstractComponent:
        key = (name, price, number, depth)

        if not self._flyweights.get(key):
            self._flyweights[key] = Product(name, number, price)
        return self._flyweights[key]

    def create_widget(self, parent: Union[QTreeWidget, QTreeWidgetItem], product: AbstractComponent) -> AbstractWidget:
        return ProductWidget(parent, product)


class BoxFactory(AbstractFactory):
    def create_component(self, name: str, number: int, price: Decimal, depth: int) -> AbstractComponent:
        return Box(name, price, depth)

    def create_widget(self, parent: Union[QTreeWidget, QTreeWidgetItem], box: AbstractComponent) -> AbstractWidget:
        return BoxWidget(parent, box)


