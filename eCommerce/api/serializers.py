from rest_framework import serializers 
from store.models import Store, Product, ProductReviews


class StoreSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Store 
        fields = ['name', 'description', 'image']

class ProductSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Product
        fields = ['name', 'price', 'store', 'description', 'image', 'stock' ]


class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReviews
        fields = ['product', 'user', 'review', 'rating', 'date_added', 'bought'] 

