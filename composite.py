from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal


class Component:
    """Abstract class"""
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def number(self) -> int:
        pass

    @property
    @abstractmethod
    def price(self) -> Decimal:
        pass

    @name.setter
    @abstractmethod
    def name(self, name: str) -> None:
        pass

    @number.setter
    @abstractmethod
    def number(self, number: int) -> None:
        pass

    @price.setter
    @abstractmethod
    def price(self, price: Decimal) -> None:
        pass

    @abstractmethod
    def add(self, component: Component) -> None:
        pass

    @abstractmethod
    def remove(self, component: Component) -> None:
        pass

    @abstractmethod
    def is_composite(self) -> bool:
        pass