from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("test", views.test, name='test'),
    path("", views.home, name ='home'),
    path("contact",views.contact, name='contact'),
    path('success', views.success, name='success'),
    path('register', views.register, name='register'),
    path('account',views.account, name='account'),
    path('modify_account', views.modify_account, name='modify_account'),
    path('add_category', views.add_category, name='add_category'),
    path('add_product', views.add_product, name='add_product'),
    path('product/delete/<product_id>/', views.delete_product, name='delete_product'),
    path('search/', views.search, name='search'),
    path('autocomplete/', views.autocomplete_view, name='autocomplete'),
    path('product_detail/', views.view_product, name='product_detail'),
    path('modify_product/', views.modify_product, name='modify_product'),
    path('view_cart/',views.view_cart, name='view_cart'),
    path('add_to_cart/',views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/',views.remove_from_cart, name='remove_from_cart'),
    path('adjust_quantity/<item_id>/', views.adjust_quantity_view, name='adjust_quantity'),
    path('order_placed/', views.tqorder, name='order_placed'),
    path('orders', views.view_orders, name='orders'),
    path('accept_order',views.accept_order, name='accept_order'),
    path('decline_order',views.decline_order, name='decline_order'),
    path('done_order',views.done_order, name='done_order'),
    path('verify_otp', views.verify_otp, name='verify_otp'),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

