from typing import Any, Dict

from django.views.generic import (
    TemplateView,
    View
)
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.forms import modelformset_factory
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from store.cart import SessionCart
from store.serializers import (
    CartSerializer, 
    CartProductAddSerializer
)
from store.forms import (
    CustomerDataForm,
    ProductCategoryParamValueForm,
    ProductCategoryParamFormset
)
from store.models import (
    Order,
    Product,
    ProductTemplate,
    ProductCategoryParamValue
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
    
    # TODO - test this, currently not in use
    @action(detail=False, methods=["get"], url_path="list-products")
    def list_products(self, request):
        # get cart items
        cart = SessionCart(self.request)
        items = cart.get_items()
        serializer = CartSerializer(instance=items, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["post"])
    def add_product(self, request):
        cart = SessionCart(self.request)
        serializer = CartProductAddSerializer(data=request.POST)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        serializer.save(cart)
        items = cart.get_items()
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

        items = cart.get_items()
        serializer = CartSerializer(instance=items, many=True)
        return Response(serializer.data, status=201)

    @action(detail=True, methods=["put"])
    def update_product(self, request, pk):
        cart = SessionCart(self.request)
        try:
            cart.update_item_quantity(pk, int(request.data["quantity"]))
        except Product.DoesNotExist:
            return Response({"error": "Product does not exist"}, status=404)
        items = cart.get_items()
        serializer = CartSerializer(instance=items, many=True)
        return Response(serializer.data, status=201)


class ConfigureProductView(View):
    template_name = "store/configure_product.html"

    def get_context_data(self, pk: int, **kwargs: Any) -> Dict[str, Any]:
        template = ProductTemplate.objects.get(pk=pk)
        category_params = template.category.category_params.all()
        formset_class = modelformset_factory(
            ProductCategoryParamValue,
            form=ProductCategoryParamValueForm, 
            formset=ProductCategoryParamFormset
        )
        formset = formset_class(queryset=category_params)
        context = {
            "template": template,
            "available_variants": Product.objects.filter(template__pk=pk),
            "category_params": category_params,
            "formset": formset
        }
        
        return context

    def get(self, request, pk: int, *args, **kwargs):
        context = self.get_context_data(pk)
        return render(request, self.template_name, context)

    def post(self, request, pk: int, *args, **kwargs):
        # first select template
        template = ProductTemplate.objects.get(pk=pk)
        category_params = template.category.category_params.all()
        params_values = []
        formset_class = modelformset_factory(
            ProductCategoryParamValue,
            form=ProductCategoryParamValueForm, 
            formset=ProductCategoryParamFormset
        )
        formset = formset_class(queryset=category_params, data=request.POST)
        print(request.POST)
        if not formset.is_valid():
            print(formset.errors)
            messages.error(request, "Niepoprawne dane")
            context = self.get_context_data(pk)
            context["formset"] = formset
            return render(request, self.template_name, context)

        for form in formset.forms:
            if not form.is_valid():
                messages.error(request, "Niepoprawne dane")
                context = self.get_context_data(pk)
                context["formset"] = formset
                return render(request, self.template_name, context)
            params_values.append(form.save())
        
        product_variant = Product.objects.get_or_create_by_params(
            template=ProductTemplate.objects.get(pk=pk), params=params_values
        )
        if not product_variant:
            messages.error(request, "Nie udało się utworzyć wariantu produktu")
            return HttpResponseRedirect(reverse("product-configure", kwargs={"pk": pk}))

        return HttpResponseRedirect(
            reverse("product-configure-summary", kwargs={"variant_pk": product_variant.pk})
        )


class ConfigureProductSummaryView(View):
    template_name = "store/configure_product_summary.html"
    
    def get(self, request, variant_pk: int, *args, **kwargs):
        variant = Product.objects.get(pk=variant_pk)
        context = {
            "variant": variant,
            "params_values": variant.params.all()
        }
        return render(request, self.template_name, context)


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
        customer_data = form.data
        # TODO - add encryption
        request.session["customer_data"] = customer_data
        return HttpResponseRedirect(reverse("order-confirm"))


class OrderConfirmView(View):
    template_name = "store/order_confirm.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        customer_data = self.request.session["customer_data"]
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
        customer_data = request.session["customer_data"]
        cart = SessionCart(self.request)
        Order.objects.create_from_cart(
            cart.get_items(), 
            None, customer_data
        )
        request.session.pop("customer_data")
        cart.clear()
        messages.success(request, "Zamówienie zostało złożone, sprawdź swój email.")
        return HttpResponseRedirect(reverse("cart"))
