from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.clients, name="clients"),
    path('login/', views.login_user, name='login'),
    path('signup/', views.signup, name="signup")
]