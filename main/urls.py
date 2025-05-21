from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('shop/', views.shop, name='shop'),

    path('contact/', views.contact_view, name='contact'),

    # urls.py
    path('product/<int:game_id>/', views.product_detail, name='product_detail'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    # urls.py
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<int:game_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('order/<int:order_id>/receipt/', views.generate_pdf_receipt, name='generate_pdf'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_history, name='order_history'),
    path('search/', views.search_view, name='search'),



]