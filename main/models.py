from django.db import models
from django.utils.text import slugify


import uuid

# Create your models here.

class Debtor(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=60)

    phone = models.CharField(max_length=20)
    email = models.EmailField()

    unique_code = models.CharField(max_length=6, unique=True, blank=True, null=True)

    slug = models.SlugField(max_length=70, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.unique_code:
            self.unique_code = uuid.uuid4().hex[:6].upper()  # 12-char code, easy to type

        # Always generate slug on save
        base_slug = slugify(f"{self.first_name} {self.last_name}")
        self.slug = f"{base_slug}-{self.unique_code}"

        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Creditor(models.Model):
    name = models.CharField()
    collected = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    withdrawals = models.OneToOneField('client.WithdrawalSettings', null=True, blank=True, 
                                       on_delete=models.CASCADE, related_name="creditor")

    is_stripe_connected = models.BooleanField(default=False)
    stripe_connect_id = models.CharField(max_length=40, null=True, blank=True)

    percent_cut = models.DecimalField(max_digits=5, decimal_places=3, default=0.1)

    def __str__(self):
        return self.name
    

class Debt(models.Model):
    debtor = models.ForeignKey('Debtor', on_delete=models.CASCADE, related_name='debts')
    creditor_name = models.ForeignKey('Creditor', on_delete=models.CASCADE, related_name='debts')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest = models.DecimalField(max_digits=10, decimal_places=2)
    incur_date = models.DateField()
    description = models.CharField(max_length=200, blank=True)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    unique_code = models.CharField(max_length=12, unique=True, blank=True, null=True)

    is_settled = models.BooleanField(default=False)
    collecting = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.unique_code:
            self.unique_code = uuid.uuid4().hex[:12].upper()  # 12-char code, easy to type
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.debtor} owes {self.creditor_name}: ${self.amount}"
    
class ScheduledMessage(models.Model):
    debtor = models.ForeignKey(Debtor, on_delete=models.CASCADE)
    debt = models.ForeignKey(Debt, on_delete=models.CASCADE, default=None)
    send_time = models.DateTimeField()
    task_name = models.CharField(max_length=255, unique=True)
    message_type = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default="scheduled")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.task_name


class MessageTemplate(models.Model):
    title = models.CharField(max_length=250)
    template = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title
    
class CustomSMSTemplate(models.Model):
    title = models.CharField(max_length=250)
    template = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title

class MessageTemplateRouter(models.Model):

    user = models.OneToOneField('client.Profile', on_delete=models.CASCADE, null=True
                                        , related_name="sms_router")

    # foreign keys for the CUSTOM templates. If null, then use default
    initial = models.ForeignKey(CustomSMSTemplate, on_delete=models.SET_NULL, 
                                      null=True, blank=True, related_name="router_init")
    
    followup1 = models.ForeignKey(CustomSMSTemplate, on_delete=models.SET_NULL, 
                                      null=True, blank=True, related_name="router1")
    
    followup2 = models.ForeignKey(CustomSMSTemplate, on_delete=models.SET_NULL, 
                                      null=True, blank=True, related_name="router2")
    
    def __str__(self):
        return f"Message Router for {str(self.user)}"

    def get_template(self, message_type):

        field_map = {
            'initial': self.initial,
            'followup1': self.followup1,
            'followup2': self.followup2
        }

        custom_template = field_map.get(message_type)
        if custom_template:
            return custom_template
        
        print(message_type)
        try:
            default_template = MessageTemplate.objects.get(title=message_type)
            return default_template
        except MessageTemplate.DoesNotExist:
            # Handle case where no template exists
            return None
    
    def set_template(self, new_templates):
        field_map = {
            'initial': 'initial',
            'followup1': 'followup1',
            'followup2': 'followup2'
        }
        
        try:
            key = new_templates['key']
            draft = new_templates['draft']
            custom = getattr(self, field_map[key])
            if custom:
                # Update the template attribute of the existing CustomSMSTemplate
                custom = getattr(self, field_map[key])
                custom.template = draft
                custom.save()
            else:
                # Create a new CustomSMSTemplate and assign it to the appropriate attribute
                setattr(self, key, CustomSMSTemplate.objects.create(title=key, template=draft))
        except KeyError as e:
            raise ValueError(f"Missing required key in new_templates: {e}")


    
class Payment(models.Model):
    debt = models.OneToOneField(Debt, on_delete=models.CASCADE, related_name="payment", 
                                null=True, blank=True)
    
    date = models.DateField(auto_now_add=True)
    in_full = models.BooleanField(default=True)
    method = models.CharField(max_length=25, default="")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def save(self, *args, **kwargs):
        if self.debt and self.amount != 0.0:
            self.amount = self.debt.amount + self.debt.interest
        super().save(*args, **kwargs)

    def __str__(self):
        if self.debt:
            return f"{self.debt.debtor} paid off ${self.debt.amount} to {self.debt.creditor_name}"
        return "n/a"