from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.clients, name="clients"),
    path('login/', views.login_user, name='login'),
    path('signup/', views.signup, name="signup"),
    path('profile-edit/', views.profile_edit, name="profile-edit"),
    path('portal/', views.portal, name="portal"),
    path('portal-dashboard/', views.portal, name="portal-dashboard"),
    path('portal-settings/', views.portal, name="portal-settings"),
    path('portal-selloff/', views.portal, name="portal-selloff"),
    path('portal-support/', views.portal, name="portal-support"),
    path('portal-debtors/', views.portal_debtors, name="portal-debtors"),
    path('portal-payments/', views.portal, name="portal-payments")
]