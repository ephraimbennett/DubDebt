from django.urls import path
from . import views
from . import views_debtor
from . import views_dashboard
from . import views_settings
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.clients, name="clients"),
    path('login/', views.login_user, name='login'),
    path('signup/', views.signup, name="signup"),
    path('privacy/', views.privacy, name="privacy"),
    path('contact/', views.contact, name="contact"),
    path('terms/', views.terms, name="terms"),

    path('profile-edit/', views.profile_edit, name="profile-edit"),
    path('portal/', views.portal, name="portal"),

    path('portal-dashboard/', views_dashboard.dashboard, name="portal-dashboard"),
    path('portal-dashboard/upload/', views_dashboard.upload_file, name="portal-dashboard-upload"),

    path('portal-settings/', views_settings.settings, name="portal-settings"),
    path('portal-selloff/', views.portal, name="portal-selloff"),
    path('portal-support/', views.portal, name="portal-support"),
    
    path('portal-payments/', views.portal, name="portal-payments"),

    path('portal-debtors/', views.portal_debtors, name="portal-debtors"),
    path('portal-debtors/edit-debt/', views_debtor.debt_edit, name="debt-edit"),
    path('portal-debtors/collect-debt/', views_debtor.debt_collect, name='debt-collect'),
    path('portal-debtors/pause-debt/', views_debtor.debt_pause, name="debt-pause")

]