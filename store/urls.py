from django.urls import path
from . import views 
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

urlpatterns = [
    path('register/',views.register,name='register'),
    path('login/',TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),   
    path('products/',views.product_list,name='product-list'),
    path('products/<int:pk>/',views.product_detail,name='product-detail'),
    path('categories/',views.get_category_list,name='category-list'),
    path('orders/',views.Order_list,name='order-list'),
    path('carts/',views.Cart_list,name='cart-list'),
    path('carts/add/',views.add_to_cart,name='add-to-cart'),
    path('carts/remove/',views.remove_from_cart,name='remove-from-cart'),
    path('carts/update/',views.update_cart_item,name='update-cart-item'),
    path('orders/create/',views.create_order,name='create-order'),

]