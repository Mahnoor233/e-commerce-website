from django.urls import path
from . import api_views

urlpatterns = [
    path('register/', api_views.RegisterAPI.as_view(), name='api_register'),
    path('products/', api_views.ProductListAPI.as_view(), name='api_product_list'),
    path('products/<int:pk>/', api_views.ProductDetailAPI.as_view(), name='api_product_detail'),
    path('orders/', api_views.OrderListAPI.as_view(), name='api_order_list'),
]
