from django.db import models
import uuid

# Create your models here.

class Debtor(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=60)

    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)

    unique_code = models.CharField(max_length=12, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.unique_code:
            self.unique_code = uuid.uuid4().hex[:12].upper()  # 12-char code, easy to type
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Creditor(models.Model):
    name = models.CharField()
    collected = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

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

    def __str__(self):
        return f"{self.debtor} owes {self.creditor_name}: ${self.amount}"