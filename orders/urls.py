from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('order/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/', views.order_history, name='order_history'),
    path('my-library/', views.my_library, name='my_library'),
    path('download/<int:pk>/', views.download_book, name='download_book'),
]
