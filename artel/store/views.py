from django.http import JsonResponse
from django.views import View


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
        try:
            product_id = request.POST.get('product_id')
            quantity = request.POST.get('quantity')
            cart = request.session.get('cart', {})
            cart[product_id] = quantity
            request.session['cart'] = cart

            return JsonResponse({'message': 'Item added to cart.'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    def delete(self, request, cart_item_id):
        cart = request.session.get('cart', {})
        if cart_item_id in cart:
            del cart[cart_item_id]
        request.session['cart'] = cart

        return JsonResponse({'message': 'Item removed from cart.'})
