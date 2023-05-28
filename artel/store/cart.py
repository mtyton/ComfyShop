from abc import (
    ABC,
    abstractmethod
)
from typing import List
from dataclasses import dataclass
from django.http.request import HttpRequest
from django.conf import settings

from store.models import Product


@dataclass
class CartItem:
    product: Product
    quantity: int


class BaseCart(ABC):

    def validate_item_id(self, item_id):
        return Product.objects.get(id=item_id)

    @abstractmethod
    def add_item(self, item_id, quantity):
        ...
    
    @abstractmethod
    def remove_item(self, item_id):
        ...

    @abstractmethod
    def update_item_quantity(self, item_id, change):
        ...
    
    @abstractmethod
    def get_items(self):
        ...


class SessionCart(BaseCart):

    def __init__(self, request: HttpRequest) -> None:
        super().__init__()
        self.session = request.session
        if not self.session.get(settings.CART_SESSION_ID):
            self.session[settings.CART_SESSION_ID] = {}

    def add_item(self, item_id: int, quantity: int) -> None:
        # TODO - add logging
        self.validate_item_id(item_id)
        quantity = int(quantity)
        item_id = int(item_id)

        if not self.session[settings.CART_SESSION_ID].get(item_id):
            self.session[settings.CART_SESSION_ID][item_id] = quantity
        else:
            self.update_item_quantity(item_id, quantity)

    def remove_item(self, item_id: int) -> None:
        self.validate_item_id(item_id)
        try:
            self.session[settings.CART_SESSION_ID].pop(item_id)
        except KeyError:
            # TODO - add logging
            ...
    
    def update_item_quantity(self, item_id: int, change: int) -> None:
        self.validate_item_id(item_id)
        try:
            self.session[settings.CART_SESSION_ID][item_id] += change
        except KeyError:
            # TODO - add logging
            self.add_item(item_id, change)

    def get_items(self) -> List[CartItem]:
        _items = []
        for item_id, quantity in self.session[settings.CART_SESSION_ID].items():
            _items.append(CartItem(quantity=quantity, product=Product.objects.get(id=item_id)))
        return _items

    @property
    def total_price(self):
        total = 0
        for item in self.get_items():
            total += item.product.price * int(item.quantity)
        return total