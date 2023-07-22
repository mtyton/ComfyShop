from abc import (
    ABC,
    abstractmethod
)
from typing import (
    List,
    Any
)
from dataclasses import dataclass
from django.http.request import HttpRequest
from django.conf import settings
from django.core import signing

from store.models import (
    Product,
    ProductAuthor
)


class BaseCart(ABC):

    def validate_and_get_product(self, item_id):
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
        self._cart = self.session.get(settings.CART_SESSION_ID, None)
        if not self._cart:
            self._cart = {}
            self.session[settings.CART_SESSION_ID] = self._cart

    def save_cart(self):
        self.session[settings.CART_SESSION_ID] = self._cart
        self.session.modified = True

    def add_item(self, item_id: int, quantity: int) -> None:
        # TODO - add logging
        product = self.validate_and_get_product(item_id)
        author = product.author
        quantity = int(quantity)
        item_id = int(item_id)
        if not self._cart.get(str(author.id)):
            self._cart[str(author.id)] = {str(item_id): quantity}
            self.save_cart()
        elif not self._cart[str(author.id)].get(str(item_id)):
            self._cart[str(author.id)].update({str(item_id): quantity})
            self.save_cart()
        else:
            new_quantity = self._cart[str(author.id)][str(item_id)] + quantity
            self.update_item_quantity(item_id, new_quantity)

    def remove_item(self, item_id: int) -> None:
        product = self.validate_and_get_product(item_id)
        author = product.author
        try:
            self._cart[str(author.id)].pop(str(item_id))
            self.save_cart()
        except KeyError:
            # TODO - add logging
            ...
    
    def update_item_quantity(self, item_id: int, new_quantity: int) -> None:
        product = self.validate_and_get_product(item_id)
        author = product.author
        if new_quantity < 1:
            self.remove_item(item_id)
            return
        if not self._cart.get(str(author.id)):
            self.add_item(item_id, new_quantity)
            return
        self._cart[str(author.id)][str(product.id)] = new_quantity
        self.save_cart()

    def get_items(self) -> List[dict[str, dict|str]]:
        items: List[dict[str, dict|str]] = []
        for author_id, cart_items in self._cart.items():
            author = ProductAuthor.objects.get(id=int(author_id))
            products = []
            for item_id, quantity in cart_items.items():
                product=Product.objects.get(id=int(item_id))
                products.append({"product": product, "quantity": quantity})
            items.append({"author": author, "products": products})
        return items

    @property
    def total_price(self):
        total = 0
        for _, cart_items in self._cart.items():
            for item_id, quantity in cart_items.items():
                product = Product.objects.get(id=int(item_id))
                total += product.price * quantity
        return total
    
    def is_empty(self) -> bool:
        return not bool(self._cart.items())

    def clear(self) -> None:
        self._cart = {}
        self.save_cart()


class CustomerData:
    
    def _encrypt_data(self, data: dict[str, Any]) -> str:
        signer = signing.Signer()
        return signer.sign_object(data)

    def _decrypt_data(self, data: str) -> dict[str, Any]:
        signer = signing.Signer()
        return signer.unsign_object(data)

    def __init__(self, data: dict[str, Any]=None, encrypted_data: str=None) -> None:
        self._data = self._encrypt_data(data) if data else encrypted_data
    
    @property
    def data(self) -> dict[str, Any]:
        return self._data
    
    @property
    def decrypted_data(self) -> dict[str, Any]:
        return self._decrypt_data(self._data)
