from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from .forms import UserRegisterForm
from .models import Product, Order, OrderItem
from .cart import Cart

import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

# Homepage view
def home(request):
    return render(request, 'store/home.html')


# Register
def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'store/register.html', {'form': form})


# Login
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        return render(request, 'store/login.html', {'error': 'Invalid credentials'})
    return render(request, 'store/login.html')


# Logout
def logout_view(request):
    logout(request)
    return redirect('login')


# Product listing
def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})


# Product detail
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})


# Cart detail
def cart_detail(request):
    cart = Cart(request)
    return render(request, 'store/cart.html', {'cart': cart})


# Add to cart
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product=product)
    return redirect('cart_detail')


# Remove from cart
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')


# Stripe checkout
def create_checkout_session(request):
    cart = Cart(request)
    total = cart.get_total_price()
    
    if total < 0.5:
        return render(request, 'store/cart.html', {
            'cart': cart,
            'error': 'Total must be at least $0.50 to proceed to checkout.'
        })

    line_items = []
    for item in cart:
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': item['product'].name},
                'unit_amount': int(float(item['price']) * 100),
            },
            'quantity': item['quantity'],
        })

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url='http://127.0.0.1:8000/success/',
        cancel_url='http://127.0.0.1:8000/cancel/',
    )
    return redirect(checkout_session.url)


# Payment success
@login_required
def success(request):
    cart = Cart(request)
    if not cart:
        return redirect('product_list')

    order = Order.objects.create(
        user=request.user,
        total_amount=cart.get_total_price(),
        is_paid=True
    )

    for item in cart:
        OrderItem.objects.create(
            order=order,
            product=item['product'],
            quantity=item['quantity'],
            price=item['price']
        )

    cart.clear()
    return render(request, 'store/success.html', {'order': order})


# Cancel page
def cancel(request):
    return render(request, 'store/cancel.html')


# Order history
@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/order_history.html', {'orders': orders})
