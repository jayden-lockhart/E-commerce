from rest_framework.response import Response
from django.http import JsonResponse
from store.models import Store, Product, ProductReviews
from .serializers import (
    StoreSerializer,
    serializers,
    ProductSerializer,
    ProductReviewSerializer,
)
from rest_framework.decorators import (
    api_view,
    renderer_classes,
    authentication_classes,
    permission_classes,
)
from django.views.decorators.csrf import csrf_exempt
from rest_framework_xml.renderers import XMLRenderer
from rest_framework import status
from store.decorators import allowed_users
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import permission_required


def basic_api_response(request):
    if request.method == "GET":
        data = serializers.serialize('json', Store.objects.all())
        return JsonResponse(data=data, safe=False)


@api_view(['GET'])
@renderer_classes((XMLRenderer,))
def view_stores(request):
    '''returns all stores in the database in xml format'''
    stores = Store.objects.all()
    serializer = StoreSerializer(stores, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
@permission_required('add_stores')
def add_store(request):
    '''adds a store to the database'''
    serializer = StoreSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@renderer_classes((XMLRenderer,))
def view_products(request):
    '''returns all products in the database in xml format'''
    product = Product.objects.all()
    serializer = ProductSerializer(product, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
@permission_required('add_products')
def add_product(request):
    '''adds a product to the database'''
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@renderer_classes((XMLRenderer,))
def view_product_reviews(request):
    '''returns all product reviews in the database in xml format'''
    reviews = ProductReviews.objects.all()
    serializer = ProductReviewSerializer(reviews, many=True)
    return Response(serializer.data)
