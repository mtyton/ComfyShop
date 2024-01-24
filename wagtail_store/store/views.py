from typing import Any, Dict

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import TemplateView, View
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from store.cart import CustomerData, SessionCart
from store.forms import CustomerDataForm, ProductTemplateConfigForm
from store.models import Order, Product, ProductListPage, ProductTemplate
from store.serializers import CartProductAddSerializer, CartSerializer
from store.tasks import send_produt_request_email


class CartView(TemplateView):
    """
    This view should simply render cart with initial data, it'll do that each refresh, for
    making actions on cart (using jquery) we will use CartActionView, which will
    be prepared to return JsonResponse.
    """

    template_name = "store/cart.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["cart"] = SessionCart(self.request)
        return context


class CartActionView(ViewSet):
    # NOTE - currently not in use
    @action(detail=False, methods=["get"], url_path="list-products")
    def list_products(self, request):
        # get cart items
        cart = SessionCart(self.request)
        items = cart.display_items
        serializer = CartSerializer(instance=items, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def add_product(self, request):
        cart = SessionCart(self.request)
        serializer = CartProductAddSerializer(data=request.POST)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        serializer.save(cart)
        items = cart.display_items
        serializer = CartSerializer(instance=items, many=True)
        return Response(serializer.data, status=201)

    @action(detail=False, methods=["post"])
    def remove_product(self, request):
        cart = SessionCart(self.request)
        product_id = request.POST.get("product_id")
        try:
            cart.remove_item(product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product does not exist"}, status=400)

        items = cart.display_items
        serializer = CartSerializer(instance=items, many=True)
        return Response(serializer.data, status=201)

    @action(detail=True, methods=["put"])
    def update_product(self, request, pk):
        cart = SessionCart(self.request)
        try:
            cart.update_item_quantity(pk, int(request.data["quantity"]))
        except Product.DoesNotExist:
            return Response({"error": "Product does not exist"}, status=404)
        items = cart.display_items
        serializer = CartSerializer(instance=items, many=True)
        return Response(serializer.data, status=201)


class ConfigureProductView(View):
    template_name = "store/configure_product.html"

    def get_context_data(self, pk: int, **kwargs: Any) -> Dict[str, Any]:
        template = get_object_or_404(ProductTemplate, pk=pk)
        form = ProductTemplateConfigForm(template=template)
        context = {"template": template, "form": form}
        return context

    def get(self, request, pk: int, *args, **kwargs):
        context = self.get_context_data(pk)
        return render(request, self.template_name, context)

    def post(self, request, pk: int, *args, **kwargs):
        # first select template
        template = get_object_or_404(ProductTemplate, pk=pk)
        form = ProductTemplateConfigForm(template=template, data=request.POST)
        if not form.is_valid():
            context = self.get_context_data(pk)
            context["form"] = form
            return render(request, self.template_name, context)

        product_variant = form.get_product()
        return HttpResponseRedirect(reverse("configure-product-summary", args=[product_variant.pk]))


class ConfigureProductSummaryView(View):
    template_name = "store/configure_product_summary.html"

    def get_context_data(self, variant_pk):
        variant = get_object_or_404(Product, pk=variant_pk)
        return {
            "variant": variant,
            "params_values": variant.params.all(),
            "store_url": ProductListPage.objects.first().get_url(),
        }

    def get(self, request, variant_pk: int, *args, **kwargs):
        context = self.get_context_data(variant_pk)
        return render(request, self.template_name, context)

    def post(self, request, variant_pk: int, *args, **kwargs):
        # Here just send the email with product request
        variant = Product.objects.get(pk=variant_pk)
        send_produt_request_email.apply_async(args=[variant.pk])
        messages.success(request, "Zapytanie o produkt zostało wysłane")
        context = self.get_context_data(variant_pk)
        return HttpResponseRedirect(context["store_url"])


class OrderView(View):
    template_name = "store/order.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = {}
        context["form"] = CustomerDataForm()
        return context

    def get(self, request, *args, **kwargs):
        cart = SessionCart(self.request)
        if cart.is_empty():
            messages.error(request, "Twój koszyk jest pusty")
            return HttpResponseRedirect(reverse("cart"))
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        cart = SessionCart(self.request)
        if cart.is_empty():
            messages.error(request, "Twój koszyk jest pusty")
            return HttpResponseRedirect(reverse("cart"))

        form = CustomerDataForm(request.POST)
        if not form.is_valid():
            context = self.get_context_data()
            context["form"] = form
            return render(request, self.template_name, context)
        customer_data = CustomerData(data=form.serialize())
        request.session["customer_data"] = customer_data.data
        return HttpResponseRedirect(reverse("order-confirm"))


class OrderConfirmView(View):
    template_name = "store/order_confirm.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        form = CustomerDataForm(data=CustomerData(encrypted_data=self.request.session["customer_data"]).decrypted_data)
        if not form.is_valid():
            raise Exception("Customer data is not valid")

        customer_data = form.cleaned_data
        return {
            "cart": SessionCart(self.request, delivery=customer_data["delivery_method"]),
            "customer_data": customer_data,
        }

    def get(self, request, *args, **kwargs):
        cart = SessionCart(self.request)
        if cart.is_empty():
            messages.error(request, "Twój koszyk jest pusty")
            return HttpResponseRedirect(reverse("cart"))
        return render(request, self.template_name, self.get_context_data())

    def post(self, request):
        customer_data = CustomerData(encrypted_data=self.request.session["customer_data"]).decrypted_data
        cart = SessionCart(self.request)
        order = Order.objects.create_from_cart(cart.display_items, None, customer_data)
        request.session.pop("customer_data")
        cart.clear()
        request.session["order_uuids"] = [str(elem) for elem in order.values_list("uuid", flat=True)]
        return HttpResponseRedirect(reverse("order-success"))


class OrderSuccessView(View):
    template_name = "store/order_success.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return {
            "orders": Order.objects.filter(uuid__in=self.request.session.get("order_uuids")),
            "store_url": ProductListPage.objects.first().get_url(),
        }

    def get(self, request, *args, **kwargs):
        if not self.request.session.get("order_uuids"):
            return HttpResponseRedirect(reverse("cart"))

        return render(request, self.template_name, self.get_context_data())
