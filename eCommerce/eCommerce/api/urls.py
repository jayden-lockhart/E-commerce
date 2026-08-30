from django.urls import path
from . import views

urlpatterns = [
    path('api_reponse', views.basic_api_response, name='api_response'),
    path('get/stores', views.view_stores, name='view_stores'),
    path('post/add_stores', views.add_store),
    path('get/products', views.view_products),
    path('post/add_product', views.add_product),
    path('get/reviews', views.view_product_reviews)
]