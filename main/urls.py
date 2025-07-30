from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('balance/', views.balance_redirect, name='balance_redirect'),
    path('balance/<str:slug>/', views.balance, name='balance'),
    path('verify/', views.verify, name='verify'),
    path('payment/<str:name>/<str:code>/', views.payment, name='payment'),
    path('payment/route/<str:code>', views.pay_debt, name='pay_route'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('api/sms/send/', views.sms_send_view, name='sms_send'),
    path('payment-success/<str:code>/', views.payment_success, name='payment-success')
]