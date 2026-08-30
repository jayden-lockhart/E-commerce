from django.shortcuts import render, get_object_or_404

from .cart import Cart
from store.models import Product, Profile, Order, OrderItem
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.core.mail import send_mail
from django.core.mail import BadHeaderError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from store.decorators import allowed_users
from django.shortcuts import redirect
from store.forms import UserInfoForm
from django.contrib.auth.models import User

# Create your views here.


def send_email(current_user):
    subject = "Order confirmation email"
    message = "Hello! This is a order confirmation email sent from E-commerce."
    recipient_list = [current_user.email]
    if not subject or not message or not recipient_list:
        return HttpResponseBadRequest("Missing email parameters.")
    try:
        send_mail(
            subject,
            message,
            None,  # Uses DEFAULT_FROM_EMAIL
            recipient_list,
            fail_silently=False,
        )
        return HttpResponse("Email sent successfully!")
    except BadHeaderError:
        return HttpResponseBadRequest("Invalid header found.")
    except Exception as e:
        return HttpResponse(f"Error sending email: {e}")


@login_required(login_url='login')
@allowed_users(allowed_roles=['buyer'])
def cart_summary(request):
    '''goes to cart summary page'''
    cart = Cart(request)
    cart_products = cart.get_products()
    quantities = cart.get_quantities()
    total_price = cart.get_total_price()
    for product in cart_products:
        count = 1
        while count <= product.stock:
            count += 1
            return render(request, 'cart/cart_summary.html', {'cart_products': cart_products, 'quantities': quantities, 'total_price': total_price, 'count': count})
    return render(request, 'cart/cart_summary.html', {'cart_products': cart_products, 'quantities': quantities, 'total_price': total_price, 'count': count})


@login_required(login_url='login')
@allowed_users(allowed_roles=['buyer'])
def cart_add(request,):
    '''adds item to cart'''
    # get cart object
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
        product = get_object_or_404(Product, id=product_id)
        cart.add(product=product, quantity=product_qty)
        # return JsonResponse({'Product Name': product.name})
        # get the total number of items in the cart
        cart_quantity = cart.__len__()
        response = JsonResponse({'qty': cart_quantity})
        messages.success(request, f"{product.name} has been added to your cart.")
        return response


@login_required(login_url='login')
@allowed_users(allowed_roles=['buyer'])
def cart_delete(request):
    '''removes item from cart'''
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        cart.delete(product=product_id)
        response = JsonResponse({'product': product_id})
        messages.success(request, "Item has been removed from your cart.")
        return response


@login_required(login_url='login')
@allowed_users(allowed_roles=['buyer'])
def cart_update(request):
    '''updates the cart'''
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
        cart.update(product=product_id, quantity=product_qty)
        response = JsonResponse({'qty': product_qty, })
        messages.success(request, "Your cart has been updated.")
        return response

    
def checkout(request):
    '''checks out the cart'''
    cart = Cart(request)
    cart_products = cart.get_products()
    quantities = cart.get_quantities()
    total_price = cart.get_total_price()
    if request.user.is_authenticated:
        current_user = Profile.objects.get(user__id=request.user.id)
        shipping_form = UserInfoForm(request.POST or None, instance=current_user)
    return render(request, 'cart/checkout.html', {'cart_products': cart_products, 'quantities': quantities, 'total_price': total_price, 'shipping_form':shipping_form})


def process_order(request):
    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_products()
        quantities = cart.get_quantities()
        total_price = cart.get_total_price()
        current_user = Profile.objects.get(user__id=request.user.id)
        form = UserInfoForm(request.POST or None, instance=current_user)
        if form.is_valid():
            form.save()
        address1 = current_user.address1
        address2 = current_user.address2
        city = current_user.city
        country = current_user.country
        post_code = current_user.post_code
        shipping_address = f'{address1}\n{address2}\n{city}\n{country}\n{post_code}'
        full_name = current_user.full_name
        email = current_user.email
        amount_paid = total_price
        if request.user.is_authenticated:
            user = request.user
            create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()

            order_id = create_order.pk
            for product in cart_products:
                product_id = product.id
                price = product.price
                for key, value in quantities.items():
                    if int(key) == product.id:
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, user=user, quantity=value, price=price)
                        create_order_item.save()
                        stock = int(product.stock)
                        qty = int(value)
                        new_stock = stock - qty
                        product.stock = new_stock
                        product.save()
            for key in list(request.session.keys()):
                if key == 'session_key':
                    del request.session[key]

        messages.success(request, 'order placed')
        send_email(current_user)
        return redirect('home')
    else:
        messages.success(request, 'Access denied!')
        return redirect('home')
