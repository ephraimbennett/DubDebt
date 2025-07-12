from django.contrib import admin
from .models import Debtor, Creditor, Debt

# Register your models here.

admin.site.register(Debtor)
admin.site.register(Creditor)
admin.site.register(Debt)