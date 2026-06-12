from itertools import product
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Product,Order,Category,Cart,CartItem,OrderItem
from .serializer import ProductSerializer,OrderSerializer,CategorySerializer,CartSerializer,CartItemSerializer
from django.contrib.auth.models import User
from .serializer import UserRegistrationSerializer,UserSerializer
from rest_framework import status    

@api_view(['GET'])
@permission_classes([AllowAny])
def product_list(request):
    products=Product.objects.all()
    serializer=ProductSerializer(products,many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def product_detail(request,pk):
    try:
        product=Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({'error':'Product not found'},status=404)
    serializer=ProductSerializer(product)
    return Response(serializer.data)    

@api_view(['GET'])
def get_category_list(request):
    categories=Category.objects.all()
    serializer=CategorySerializer(categories,many=True)
    return Response(serializer.data)
@api_view(['GET'])
def Order_list(request):
    orders=Order.objects.all()
    serializer=OrderSerializer(orders,many=True)
    return Response(serializer.data) 

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Cart_list(request):
    cart, created = Cart.objects.get_or_create(user=request.user)

    serializer = CartSerializer(cart)

    total_price = sum(
        float(item.price) * item.quantity
        for item in cart.items.all() # type: ignore
    )

    return Response({
        "items": serializer.data["items"], # type: ignore
        "total_price": total_price
    })    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    
    print("USER:", request.user)
    print("AUTH:", request.user.is_authenticated)
    user = request.user

    product_id = request.data.get('product_id')
    quantity = int(request.data.get('quantity', 1))

    product = get_object_or_404(Product, id=product_id)

    cart, created = Cart.objects.get_or_create(user=user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={
            'quantity': quantity,
            'price': product.price
        }
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    return Response({'message': 'Product added to cart'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_cart_item(request):
    item_id=request.data.get('item_id')
    quantity=int(request.data.get('quantity',1))
    cart_item = CartItem.objects.filter(
    id=item_id,
    cart__user=request.user
).first()
    if cart_item:
        cart_item.quantity=quantity
        cart_item.save()
        return Response({'message':'Cart item updated'})
    else:
        return Response({'error':'Cart item not found'},status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request):
    item_id=request.data.get('item_id')
    cart_item=CartItem.objects.filter(id=item_id).delete()
    return Response({'message':'Product removed from cart'})
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    try:
        data = request.data
        name = data.get('name')
        address = data.get('address')
        phone = data.get('phone')
        payment_method = data.get('payment_method', 'COD')
        
        if len(phone) != 10:
         return Response( {'error': 'Invalid phone number'}, status=status.HTTP_400_BAD_REQUEST)
        
        cart,created = Cart.objects.get_or_create(user=request.user)
        if cart.items.count() == 0:#type: ignore
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        total_amount = sum(item.product.price * item.quantity for item in cart.items.all())#type: ignore
        
        order = Order.objects.create(
            user=request.user,
            total_amount=total_amount
        )   
        for item in cart.items.all():#type: ignore
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.price
            )
        cart.items.all().delete()#type: ignore
        return Response({'message': 'Order created successfully'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        
        
@api_view(['POST'])
@permission_classes([AllowAny])  
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

