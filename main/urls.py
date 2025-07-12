from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('balance/', views.balance, name='balance'),
    path('verify/', views.verify, name='verify')
]