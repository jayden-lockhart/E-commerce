from .cart import Cart

# Context processor to make the cart available in all templates
def cart(request):
    return {'cart': Cart(request)}