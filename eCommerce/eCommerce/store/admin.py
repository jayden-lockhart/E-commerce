from django.contrib import admin
from .models import Store, Customer, Product, Order, Profile, OrderItem, ShippingAddress, ProductReviews
from django.contrib.auth.models import User

# Register your models here.
admin.site.register(Store)
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Profile)
admin.site.register(ShippingAddress)
admin.site.register(ProductReviews)


class ProfileInLine(admin.StackedInline):
    model = Profile

class UserAdmin(admin.ModelAdmin):
    model = User
    field = ['username', 'first_name', 'last_name', 'email']
    inlines = [ProfileInLine]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    model = Order
    readonly_fields = ['date_ordered']
    fields = ['user', 'full_name', 'email', 'shipping_address', 'amount_paid', 'date_ordered']
    inlines = [OrderItemInline]

admin.site.unregister(Order)
admin.site.register(Order, OrderAdmin)