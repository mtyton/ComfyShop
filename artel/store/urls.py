from django.urls import path
from rest_framework.routers import DefaultRouter

from store import views as store_views


router = DefaultRouter()
router.register("cart-action", store_views.CartActionView, "cart-action")


urlpatterns = [
    path('product-configure/<int:pk>/', store_views.ConfigureProductView.as_view(), name='product-configure'),
    path('cart/', store_views.CartView.as_view(), name='cart'),
    path("order/", store_views.OrderView.as_view(), name="order"),
    path("order/confirm/", store_views.OrderConfirmView.as_view(), name="order-confirm")
] + router.urls
