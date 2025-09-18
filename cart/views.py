from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from movies.models import Movie
from .utils import calculate_cart_total
from .models import Order, Item
from django.contrib.auth.decorators import login_required

def index(request):
    cart_number = int(request.GET.get('cart_number', 1))
    cart_key = f"cart_{cart_number}"
    cart_total = 0
    movies_in_cart = []
    cart = request.session.get(cart_key, {})
    movie_ids = list(cart.keys())
    if movie_ids:
        movies_in_cart = Movie.objects.filter(id__in=movie_ids)
        cart_total = calculate_cart_total(cart, movies_in_cart)
    template_data = {
        'title': f'Cart {cart_number}',
        'movies_in_cart': movies_in_cart,
        'cart_total': cart_total,
        'cart_number': cart_number,
        'cart': cart
    }
    return render(request, 'cart/index.html', {'template_data': template_data})

from django.contrib.auth.decorators import login_required

@login_required
def add(request, id):
    get_object_or_404(Movie, id=id)
    cart_number = int(request.POST.get('cart_number', 1))
    cart_key = f"cart_{cart_number}"
    cart = request.session.get(cart_key, {})
    cart[id] = request.POST['quantity']
    request.session[cart_key] = cart
    return redirect(f'/cart/?cart_number={cart_number}')

def clear(request):
    cart_number = int(request.POST.get('cart_number', 1))
    cart_key = f"cart_{cart_number}"
    request.session[cart_key] = {}
    return redirect(f'/cart/?cart_number={cart_number}')

@login_required
def purchase(request):
    cart_number = int(request.POST.get('cart_number', 1))
    cart_key = f"cart_{cart_number}"
    cart = request.session.get(cart_key, {})
    movie_ids = list(cart.keys())
    if not movie_ids:
        return redirect(f'/cart/?cart_number={cart_number}')
    movies_in_cart = Movie.objects.filter(id__in=movie_ids)
    cart_total = calculate_cart_total(cart, movies_in_cart)
    order = Order()
    order.user = request.user
    order.total = cart_total
    order.cart_number = cart_number
    order.save()
    for movie in movies_in_cart:
        item = Item()
        item.movie = movie
        item.price = movie.price
        item.order = order
        item.quantity = cart[str(movie.id)]
        item.save()
    request.session[cart_key] = {}
    template_data = {
        'title': 'Purchase confirmation',
        'order_id': order.id,
        'cart_number': cart_number
    }
    return render(request, 'cart/purchase.html', {'template_data': template_data})