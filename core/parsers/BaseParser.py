from abc import abstractmethod, ABCMeta


class BaseParser(metaclass=ABCMeta):

    @abstractmethod
    def process(self):
        pass
