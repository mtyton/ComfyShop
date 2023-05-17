from django.shortcuts import render, redirect


def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST["product_id"]
    cart = request.session['cart']
    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1

    # Save the session
    request.session.modified = True
    return redirect('../cart/items')


def remove_from_cart(request):
    if request.method == 'POST':
        product_id = request.POST["product_id"]
    cart = request.session.get('cart', {})
    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart
        request.session.modified = True

    # Redirect to the cart page or product listing page
    return redirect('../cart/items')


def view_cart(request):
    cart = request.session.get('cart', {})
    products = "good"
    return render(request, 'store/cart_items.html',
                  {'cart': cart, 'products': products})
