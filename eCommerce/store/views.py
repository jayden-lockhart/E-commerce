from django.shortcuts import redirect, render
from .models import Product, Store, Profile, OrderItem, ProductReviews
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.forms import UserCreationForm
from .forms import (
    SignUpForm,
    UpdateUserForm,
    ChangePassword,
    UserInfoForm,
    StoreForm,
    ProductForm,
    ReviewForm,
)
from django import forms
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users, vendor_only
from django.core.mail import EmailMessage
from django.utils import timezone
from datetime import datetime, timedelta
from hashlib import sha1
import secrets
from django.core.exceptions import ObjectDoesNotExist
from .utils import generate_reset_url, build_email 
from .models import ResetToken
from django.db import IntegrityError
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.hashers import make_password
import json
from cart.cart import Cart
from django.contrib.contenttypes.models import ContentType


# Create your views here.
@unauthenticated_user
def register(request):
    '''registers a new user'''
    form = SignUpForm()
    try:
        if request.method == 'POST':
            store_content_type = ContentType.objects.get_for_model(Store)
            product_content_type = ContentType.objects.get_for_model(Product)
            form = SignUpForm(request.POST)
            email = request.POST.get('email')
            if User.objects.filter(email=email).exists():
                messages.error(request, 'That email is already in use')
            if form.is_valid():
                user = form.save()
                login(request, user)
                buyer, created = Group.objects.get_or_create(
                    name='buyer'
                )
                vendor, created = Group.objects.get_or_create(
                    name='vendor'
                )
                permission1, created = Permission.objects.get_or_create(
                    codename='can_add_store',
                    name='Can add stores',
                    content_type=store_content_type
                )
                permission2, created = Permission.objects.get_or_create(
                    codename='can_add_product',
                    name='Can add product',
                    content_type=product_content_type
                )
                vendor.permissions.add(permission1)
                vendor.permissions.add(permission2)
                current_user = User.objects.get(id=request.user.id)
                role = form.cleaned_data['role']
                if role == 'vendor':
                    current_user.groups.add(vendor)
                elif role == 'buyer':
                    current_user.groups.add(buyer)
                Profile.objects.create(
                    user=current_user,
                    email=current_user.email
                )
                messages.success(request, "Registration successful.")
                return redirect('home')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return render(
                        request,
                        'store/register.html',
                        {'form': form}
                    )
    except Exception as e:
        messages.error(f"An error occurred: {e}")
        return render(request, 'store/register.html', {'form': form})
    else:
        return render(request, 'store/register.html', {'form': form})


@login_required(login_url='login')
def product(request, pk):
    '''goes to specific product page'''
    product = Product.objects.get(id=pk)
    quantity = range(1, product.stock + 1)
    if request.method == 'POST':
        rating = request.POST.get('rating', 3)
        review = request.POST.get('review', '')
        if review:
            if OrderItem.objects.filter(product=product, user=request.user):
                ProductReviews.objects.create(
                    product=product,
                    rating=rating,
                    review=review,
                    user=request.user,
                    bought=True
                )
            else:
                ProductReviews.objects.create(
                    product=product,
                    rating=rating,
                    review=review,
                    user=request.user,
                    bought=False
                )
            return redirect('home')
    else:
        form = ReviewForm()
    return render(
        request,
        'store/product.html',
        {'product': product, 'form': form, 'quantity': quantity},
    )


@login_required(login_url='login')
def store_summary(request):
    '''goes to store summary page'''
    stores = Store.objects.all()
    return render(request, 'store/store_summary.html', {'stores': stores})


@login_required(login_url='login')
def store(request, pk):
    '''goes to specific store page'''
    pk = pk.replace('-', ' ')
    try:
        store = Store.objects.get(name=pk)
        products = Product.objects.filter(store=store)
        return render(
            request,
            'store/store.html',
            {'products': products, 'store': store},
        )
    except Store.DoesNotExist:
        messages.success(request, "store not found.")
        return redirect('home')


@login_required(login_url='login')
def home(request):
    '''goes to home page'''
    products = Product.objects.all()
    return render(request, 'store/home.html', {'products': products})


@login_required(login_url='login')
def about(request):
    '''goes to about page'''
    return render(request, 'store/about.html')


@unauthenticated_user
def login_user(request):
    '''logs user in'''
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            current_user = Profile.objects.get(user__id=request.user.id)
            saved_cart = current_user.old_cart
            if saved_cart:
                convert_cart = json.loads(saved_cart)
                cart = Cart(request)
                for key, value in convert_cart.items():
                    cart.db_add(product=key, quantity=value)
            messages.success(request, "You have been logged in.")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')
    else:
        return render(request, 'store/login.html')


def logout_user(request):
    '''logs out user'''
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')


@unauthenticated_user
def register_buyer(request):
    '''registers a new user'''
    form = SignUpForm()
    try:
        if request.method == 'POST':
            form = SignUpForm(request.POST)
            email = request.POST.get('email')
            if User.objects.filter(email=email).exists():
                messages.error(request, 'That email is already in use')
            if form.is_valid():
                user = form.save()
                login(request, user)
                buyer, created = Group.objects.get_or_create(
                    name='buyer'
                )
                current_user = User.objects.get(id=request.user.id)
                current_user.groups.add(buyer)
                Profile.objects.create(
                    user=current_user,
                    email=current_user.email
                )
                messages.success(request, "Registration successful.")
                return redirect('home')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return render(
                        request,
                        'store/register.html',
                        {'form': form}
                    )
    except IntegrityError:
        messages.error(request, 'That email is already in use')
        return render(
            request,
            'store/register.html',
            {'form': form}
        )
    else:
        return render(request, 'store/register_buyer.html', {'form': form})


def register_vendor(request):
    '''registers a new user'''
    form = SignUpForm()
    try:
        if request.method == 'POST':
            form = SignUpForm(request.POST)
            email = request.POST.get('email')
            if User.objects.filter(email=email).exists():
                messages.error(request, 'That email is already in use')

            if form.is_valid():
                user = form.save()
                login(request, user)
                vendor, created = Group.objects.get_or_create(name='vendor')
                current_user = User.objects.get(id=request.user.id)
                current_user.groups.add(vendor)
                Profile.objects.create(
                    user=current_user, email=current_user.email)
                messages.success(request, "Registration successful.")
                return redirect('home')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                return render(
                    request, 'store/register_vendor.html', {'form': form})
    except IntegrityError:
        messages.error(request, 'That email is already in use')
        return render(request, 'store/register_vendor.html', {'form': form})
    else:
        return render(request, 'store/register_vendor.html', {'form': form})


@login_required(login_url='login')
def update_user(request):
    '''updates user info'''
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance=current_user)
        if user_form.is_valid():
            user = user_form.save()
            user_type = user_form.cleaned_data.get('user_types')
            group = Group.objects.get(name=user_type)
            user.groups.add(group)
            login(request, current_user)
            messages.success(request, "Your account has been updated.")
            return redirect('home')
        return render(request, 'store/update_user.html', {'form': user_form})
    else:
        messages.error(
            request, "You must be logged in to update your account.")
        return redirect('home')


@login_required(login_url='login')
def update_password(request):
    '''updates user password'''
    if request.user.is_authenticated:
        current_user = request.user
        if request.method == 'POST':
            form = ChangePassword(current_user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password has been updated')
                # login(request, current_user)
                return redirect('login')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect('update_password')
        else:
            form = ChangePassword(current_user)
            return render(
                request, 'store/update_password.html', {'form': form})
    else:
        messages.success(request, 'You  must be logged in')
        return redirect('home')


@login_required(login_url='login')
def update_info(request):
    '''updates user info'''
    if request.user.is_authenticated:
        current_user = Profile.objects.get(user__id=request.user.id)
        form = UserInfoForm(request.POST or None, instance=current_user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your info has been updated.")
            return redirect('home')
        return render(request, 'store/update_info.html', {'form': form})
    else:
        messages.error(request, "You must be logged in to update your info.")
        return redirect('home')


@login_required(login_url='login')
@allowed_users(allowed_roles=['buyer'])
def become_vendor(request):
    '''allows user to become a vendor'''
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        current_user.groups.clear()
        group = Group.objects.get(name='vendor')
        current_user.groups.add(group)
        messages.success(request, "You are now a vendor.")
        return redirect('home')
    else:
        messages.error(request, 'You must be logged in to become a vendor.')
        return redirect('home')


@login_required(login_url='login')
def become_buyer(request):
    '''allows user to become a buyer'''
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        current_user.groups.clear()
        group = Group.objects.get(name='buyer')
        current_user.groups.add(group)
        messages.success(request, "You are now a buyer.")
        return redirect('home')
    else:
        messages.error(request, 'You must be logged in to become a buyer.')
        return redirect('home')


@login_required(login_url='login')
def add_store(request):
    '''adds a store'''
    if request.method == 'POST':
        form = StoreForm(request.POST)
        if form.is_valid():
            store = form.save(commit=False)
            store.save()
            return redirect('store_summary')
        else:
            messages.error(request, 'Invalid input. Try again')
            return redirect('add_store')
    else:
        form = StoreForm()
    return render(request, 'store/add_store.html', {'form': form})


@login_required(login_url='login')
@allowed_users(allowed_roles=['vendor'])
def edit_store(request, pk):
    '''edits specific store'''
    store = Store.objects.get(id=pk)
    form = StoreForm(instance=store)
    if request.method == 'POST':
        form = StoreForm(request.POST, instance=store)
        if form.is_valid():
            form.save()
            return redirect('store_summary')
    else:
        form = StoreForm(instance=store)
    return render(request, 'store/edit_store.html', {'form': form})


@login_required(login_url='login')
@allowed_users(allowed_roles=['vendor'])
def delete_store(request, pk):
    '''deletes specific store'''
    store = Store.objects.get(id=pk)
    if request.method == 'POST':
        store.delete()
        return redirect('store_summary')
    return render(request, 'store/delete_store.html', {'store': store})


@login_required(login_url='login')
@allowed_users(allowed_roles=['vendor'])
def add_product(request):
    '''adds a product'''
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.save()
            return redirect('store_summary')
        else:
            messages.error(request, 'Invalid input. Try again')
            return redirect('add_product')
    else:
        form = ProductForm()
    return render(request, 'store/add_product.html', {'form': form})


@login_required(login_url='login')
@allowed_users(allowed_roles=['vendor'])
def edit_product(request, pk):
    '''edits specific product'''
    product = Product.objects.get(id=pk)
    form = ProductForm(instance=product)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('store_summary')
    else:
        form = ProductForm(instance=product)
    return render(request, 'store/edit_product.html', {'form': form})


@login_required(login_url='login')
@allowed_users(allowed_roles=['vendor'])
def delete_product(request, pk):
    '''deletes specific product'''
    product = Product.objects.get(id=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('store_summary')
    return render(request, 'store/delete_product.html', {'product': product})


def add_review(request, id):
    '''adds a review to a product'''
    product = Product.objects.get(pk=id)
    user = request.user
    bought = OrderItem.objects.filter(product=product, user=user).exists()
    ProductReviews.objects.create(
        user=user,
        product=product,
        review=request.POST['review'],
        rating=request.POST['rating'],
        bought=bought,
    )
    return redirect('product', pk=product.id)
