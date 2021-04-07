from abc import ABC, abstractmethod


class Singleton(type):
    _instance = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instance:
            cls._instance[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance[cls]


class AbstractFactory(ABC, metaclass=Singleton):
    def __init__(self):
        self.x = 1
        print('AbstractFactory create')

    @abstractmethod
    def create_product(self):
        pass

    @abstractmethod
    def create_box(self):
        pass
