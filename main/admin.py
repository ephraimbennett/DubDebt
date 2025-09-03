from django.contrib import admin
from .models import Debtor, Creditor, Debt, ScheduledMessage, MessageTemplate, Payment, CustomSMSTemplate
from .models import MessageTemplateRouter, EmailTemplate, EmailCustomTemplate

# Register your models here.

admin.site.register(Debtor)
admin.site.register(Creditor)
admin.site.register(Debt)
admin.site.register(ScheduledMessage)
admin.site.register(MessageTemplate)
admin.site.register(Payment)
admin.site.register(MessageTemplateRouter)
admin.site.register(CustomSMSTemplate)
admin.site.register(EmailTemplate)
admin.site.register(EmailCustomTemplate)