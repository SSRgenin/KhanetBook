from django.urls import path
from . import views

urlpatterns = [
    path('', views.api_docs, name='api_docs'),
    path('docs/', views.api_docs, name='api_docs_alt'),
    path('health/', views.health_check_api, name='api_health'),
    path('books/', views.book_list_api, name='api_book_list'),
    path('books/<int:pk>/', views.book_detail_api, name='api_book_detail'),
    path('categories/', views.category_list_api, name='api_category_list'),
    path('cart/', views.cart_api, name='api_cart'),
    path('cart/add/<int:pk>/', views.cart_add_api, name='api_cart_add'),
    path('cart/remove/<int:pk>/', views.cart_remove_api, name='api_cart_remove'),
    path('seller/dashboard/', views.seller_stats_api, name='api_seller_dashboard'),
]
