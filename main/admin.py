from django.contrib import admin
from .models import Debtor, Creditor, Debt, ScheduledMessage, MessageTemplate

# Register your models here.

admin.site.register(Debtor)
admin.site.register(Creditor)
admin.site.register(Debt)
admin.site.register(ScheduledMessage)
admin.site.register(MessageTemplate)