from typing import Any, Dict

from django.views.generic import (
    TemplateView,
    View
)
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from store.cart import SessionCart
from store.serializers import (
    CartProductSerializer, 
    CartProductAddSerializer
)
from store.forms import CustomerDataForm
from store.models import (
    CustomerData,
    Order,
    OrderProduct,
    OrderDocument,
    DocumentTemplate
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
        serializer = CartProductSerializer(instance=items, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["post"])
    def add_product(self, request):
        cart = SessionCart(self.request)
        serializer = CartProductAddSerializer(data=request.POST)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        serializer.save(cart)

        items = cart.get_items()
        serializer = CartProductSerializer(instance=items, many=True)
        return Response(serializer.data, status=201)
    
    @action(detail=False, methods=["post"])
    def remove_product(self, request):
        cart = SessionCart(self.request)
        product_id = request.POST.get("product_id")
        cart.remove_item(product_id)

        items = cart.get_items()
        serializer = CartProductSerializer(instance=items, many=True)
        return Response(serializer.data, status=201)

    @action(detail=True, methods=["put"])
    def update_product(self, request, product_id):
        cart = SessionCart(self.request)
        product_id = request.POST.get("product_id")
        cart.update_item_quantity(product_id, request.PUT["quantity"])
        items = cart.get_items()
        serializer = CartProductSerializer(instance=items, many=True)
        return Response(serializer.data, status=201)
    

class OrderView(View):
    template_name = "store/order.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = {}
        context["form"] = CustomerDataForm()
        return context

    def get(self, request, *args, **kwargs):
        cart = SessionCart(self.request)
        if cart.is_empty():
            # TODO - messages
            return HttpResponseRedirect(reverse("cart"))
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        # TODO - messages
        cart = SessionCart(self.request)
        if cart.is_empty():
            return HttpResponseRedirect(reverse("cart"))
        form = CustomerDataForm(request.POST)
        if not form.is_valid():
            print(form.errors)
            context = self.get_context_data()
            context["form"] = form
            return render(request, self.template_name, context)
        customer_data = form.save()
        request.session["customer_data_id"] = customer_data.id
        # TODO - add this page
        return HttpResponseRedirect(reverse("order-confirm"))


class OrderConfirmView(View):
    template_name = "store/order_confirm.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        customer_data = CustomerData.objects.get(id=self.request.session["customer_data_id"])
        return {
            "cart": SessionCart(self.request),
            "customer_data": customer_data
        }

    def get(self, request, *args, **kwargs):
        cart = SessionCart(self.request)
        if cart.is_empty():
            # TODO - messages
            return HttpResponseRedirect(reverse("cart"))
        return render(request, self.template_name, self.get_context_data())

    def post(self, request):
        customer_data = CustomerData.objects.get(id=self.request.session["customer_data_id"])
        cart = SessionCart(self.request)
        order = Order.objects.create_from_cart(
            cart, customer_data
        )
        self.request.session.pop("customer_data_id")
        cart.clear()
        # TODO - messages
        return HttpResponseRedirect(reverse("cart"))


class SendMailView(View):
    def get(self, request):
        from django.core import mail
        from django.http import HttpResponse
        from django.conf import settings
        r = mail.send_mail(
            subject=f"Test",
            message="Dokumenty dla Twojego zamówienia",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=["mateusz.tyton99@gmail.com"]
        )
        return HttpResponse(f"Mail sent: {r}")
