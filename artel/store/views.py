from django.http import JsonResponse
from django.views import View
from django.shortcuts import render
import json


class CartView(View):
    def get(self, request):
        cart = request.session.get('cart', {})
        cart_items = cart.items()
        response_data = {
            'cart_items': [{
                'product_id': key,
                'quantity': value
            } for key, value in cart_items]
        }
        return JsonResponse(response_data)


class CartItemView(View):
    allowed_methods = ['POST', 'DELETE']

    def post(self, request):
            product_id = request.POST.get('product_id')
            quantity = request.POST.get('quantity')
            cart = request.session.get('cart', {})
            cart[product_id] = quantity
            request.session['cart'] = cart

            return JsonResponse({'message': 'Item added to cart.'})

    def delete(self, request, cart_item_id):
        cart = request.session.get('cart', {})
        if str(cart_item_id) in cart:
            del cart[str(cart_item_id)]
        request.session['cart'] = cart

        return JsonResponse({'message': 'Item deleted from cart.'})


class CartPageView(View):
    template_name = 'store/cart.html'

    def get(self, request):
        cart_view = CartView()
        cart_response = cart_view.get(request)
        cart_data = json.loads(cart_response.content)

        context = {
            'cart_items': cart_data['cart_items']
        }
        return render(request, self.template_name, context)
