from utils import BaseData


class Fragment(BaseData):
    """
    Mainly for the storage of temporary data,
    such as html fragment compiled from markdown.
    """
    def __init__(self, mark, data):
        super().__init__(mark, data)


class Product(BaseData):
    """
    Storing data for output.
    """
    def __init__(self, mark, data):
        super().__init__(mark, data)
