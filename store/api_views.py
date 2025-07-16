from rest_framework import generics, permissions
from django.contrib.auth.models import User
from .models import Product, Order
from .serializers import (
    RegisterSerializer, UserSerializer,
    ProductSerializer, OrderSerializer
)

# Register new users
class RegisterAPI(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

# Product list
class ProductListAPI(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# Product detail
class ProductDetailAPI(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# Order history
class OrderListAPI(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')
