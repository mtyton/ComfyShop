from django.urls import path
from rest_framework.routers import DefaultRouter

from store import views as store_views


router = DefaultRouter()
router.register("cart-action", store_views.CartActionView, "cart-action")


urlpatterns = [
    path('cart/', store_views.CartView.as_view(), name='cart'),
    # path('cart/item/<int:cart_item_id>/', store_views.CartItemView.as_view(), name='cart_item_remove'),
    # path('cart/item/', store_views.CartItemView.as_view(), name='add_to_cart'),
] + router.urls
