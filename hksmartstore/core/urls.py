from django.urls import path
from . import views
from django.shortcuts import redirect 

urlpatterns = [
    path('', views.home, name='home'),
    path('subscribe-earn/', views.subscribe_view, name='subscribe_earn'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/read/<int:pk>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/clear/', views.clear_notifications, name='clear_notifications'),
    path('coupons/', views.coupons_view, name='coupons'),
    path('become-vendor/', views.become_vendor, name='become_vendor'),
    path('search/', views.search_view, name='search'),
    path('subscribe/', views.subscribe_view, name='subscribe'),
    path('subscribe/payment/', views.subscribe_payment, name='subscribe_payment'),
    path('subscribe/success/', views.subscribe_success, name='subscribe_success'),
]


