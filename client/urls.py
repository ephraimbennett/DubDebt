from django.urls import path
from . import views
from . import views_debtor
from . import views_dashboard
from . import views_settings
from . import views_payments
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
    path('portal-dashboard/get-files/', views_dashboard.get_uploaded_files, name="dashboard-get-files"),
    path('portal-dashboard/remove-file/', views_dashboard.remove_uploaded_file, name="dashboard-remove-file"),

    path('portal-settings/', views_settings.settings, name="portal-settings"),
    path('portal-settings/stripe/', views_settings.stripe_account_link, name="stripe-account-link"),
    path('portal-settings/method-data/', views_settings.method_data, name="method-data"),

    path('portal-selloff/', views.portal, name="portal-selloff"),
    path('portal-support/', views.portal, name="portal-support"),
    
    path('portal-payments/', views_payments.payments, name="portal-payments"),
    path('portal-payments/get-payments/', views_payments.api_payments, name="payments-get"),
    path('portal-payments/add-payment/', views_payments.api_add_payment, name="payments-add"),

    path('portal-debtors/', views.portal_debtors, name="portal-debtors"),
    path('portal-debtors/edit-debt/', views_debtor.debt_edit, name="debt-edit"),
    path('portal-debtors/collect-debt/', views_debtor.debt_collect, name='debt-collect'),
    path('portal-debtors/pause-debt/', views_debtor.debt_pause, name="debt-pause")

]