from django.db import models
import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.contrib.auth.models import Group
from django.conf import settings

from django.contrib.auth.models import AbstractUser

# Create your models here.


class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=10)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.first_name + " " + self.last_name


class Profile(models.Model):
    '''profile model for user
    attributes:
    user(one to one field): the user of the profile
    full_name(charfield): the full name of the user
    email(emailfield): the users email address
    address(charfield): the addresss of the user
    address(charfield): the addresss of the user
    city(charfield): the city of th user
    country(charfield): the country of the user
    post_code(charfield): the post code of the user
    old_cart(charfield): the items left in the cart
        '''
    USER_TYPE = [
    ('vendor', 'vendor'),
    ('buyer', 'buyer')
]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(max_length=254, blank=True, unique=True)
    address1 = models.CharField(max_length=255, blank=True)
    address2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    post_code = models.CharField(max_length=10, blank=True)
    old_cart = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.user.username


# store model
class Store(models.Model):
    '''store model for vendors'''
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=500, default='', blank=True, null=True)
    image = models.ImageField(upload_to='uploads/product/', blank=True, null=True, default='#')

    def __str__(self):
        return self.name

    class meta:
        permissions = [
            ("add_stores", "can add stores")
        ]


# product model
class Product(models.Model):
    '''product model for stores'''
    name = models.CharField(max_length=100)
    price = models.DecimalField(default=0, decimal_places=2, max_digits=6)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, default=1)
    description = models.TextField(max_length=500, default='', blank=True, null=True)
    image = models.ImageField(upload_to='uploads/product/', blank=True, null=True, default='#')
    stock = models.PositiveIntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return self.name

    def stock_range(self):
        return range(1, self.stock + 1)

    class meta:
        permissions = [
            ("add_products", "can add products")
        ]


# customer orders
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=250, blank=True, null=True)
    email = models.EmailField(max_length=250, blank=True, null=True)
    shipping_address = models.TextField(max_length=15000, blank=True, null=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f'Order - {str(self.id)}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveBigIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Order Item - {str(self.id)}'


class ResetToken(models.Model):
    # Reference to the user who requested the password reset
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Token string, unique to avoid duplicates
    token = models.CharField(max_length=255, unique=True)
    # When this token expires
    expiry_date = models.DateTimeField()
    # Whether this token has already been used
    used = models.BooleanField(default=False)

    def __str__(self):
        # Show a short summary for easier debugging
        return f"ResetToken(user={self.user.username}, token={self.token[:10]}..., used={self.used})"


class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255,)
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    post_code = models.CharField(max_length=255)

    class Meta:
        def __str__(self):
            return f'Shipping Address - {str(self.id)}'


RATING = [
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
]


class ProductReviews(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    review = models.TextField(blank=True, null=True)
    rating = models.IntegerField(choices=RATING, default=5)
    date_added = models.DateTimeField(auto_now_add=True)
    bought = models.BooleanField(default=False)

    class Meta:
        def __str__(self):
            return self.product.name

    def get_rating(self):
        return self.rating

    def clean(self):
        # Verify purchase before allowing review
        if OrderItem.objects.filter(user=self.user, product=self.product).exists():
            self.bought = True
            return self.bought
