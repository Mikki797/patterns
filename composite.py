from __future__ import annotations
from PyQt5.QtWidgets import QTreeWidgetItem

from abc import ABC, abstractmethod
from typing import List
from decimal import Decimal


class Component(QTreeWidgetItem):
    def __init__(self, name: str, price: Decimal, number: int) -> None:
        super().__init__()
        self.name = name
        self._price = price
        self._number = number

        self.number = number
        self.price = price

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
    def name(self, name: str):
        self._name = name
        self.setText(0, name)

    @number.setter
    def number(self, number: int):
        self._number = number
        self.setText(1, str(number))
        self.setText(2, str(self.price*self.number))

    @price.setter
    def price(self, price: Decimal):
        self._price = price
        self.setText(2, str(self.price*self.number))

    @abstractmethod
    def add(self, component: Component) -> None:
        pass

    @abstractmethod
    def remove(self, component: Component) -> None:
        pass

    @abstractmethod
    def is_composite(self) -> bool:
        pass

    @abstractmethod
    def operation(self) -> str:
        pass

    def __str__(self):
        return f'{self.name} {self.price}р. {self.number}шт.'


class Product(Component):
    def operation(self):
        return "Product name"

    def is_composite(self) -> bool:
        return False

    def add(self, component: Component) -> None:
        pass

    def remove(self, component: Component) -> None:
        pass


class Box(Component):
    def __init__(self, name: str, price: Decimal) -> None:
        super().__init__(name, price, 1)
        self._children: List[Component] = []

    def add(self, component: Component) -> None:
        if not component.is_composite():
            for child in self._children:
                if child.name == component.name:
                    child.number += 1
                    return

        self.addChild(component)
        self._children.append(component)

    def remove(self, component: Component) -> None:
        self._children.remove(component)

    def is_composite(self) -> bool:
        return True

    def operation(self) -> str:
        results = []
        for child in self._children:
            results.append(child.operation())