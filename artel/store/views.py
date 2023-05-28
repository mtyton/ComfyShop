from typing import Any, Dict

from django.views.generic import TemplateView
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from store.cart import SessionCart
from store.serializers import (
    CartProductSerializer, 
    CartProductAddSerializer
)


class CartView(TemplateView):
    """
        This view should simply render cart with initial data, it'll do that each refresh, for 
        making actions on cart (using jquery) we will use CartActionView, which will 
        be prepared to return JsonResponse.
    """
    template_name = 'store/cart.html'


    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["cart"] = SessionCart(self.request)
        return context


class CartActionView(ViewSet):
    
    @action(detail=False, methods=["get"], url_path="list-products")
    def list_products(self, request):
        # get cart items
        cart = SessionCart(self.request)
        items = cart.get_items()
        serialzier = CartProductSerializer(instance=items, many=True)
        return Response(serialzier.data)
    
    @action(detail=False, methods=["post"])
    def add_product(self, request):
        cart = SessionCart(self.request)
        serializer = CartProductAddSerializer(data=request.POST)
        if serializer.is_valid():
            return Response(serializer.errors, status=400)
        serializer.save(cart)

        items = cart.get_items()
        serialzier = CartProductSerializer(instance=items, many=True)
        return Response(serialzier.data, status=201)
    
    # TODO - same for remove product
