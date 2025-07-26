from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.postgres.fields import ArrayField

from django.conf import settings

from django.utils.html import format_html
from google.cloud import storage
import google.auth
import os


# Create your models here.

class MemberManager(BaseUserManager):
    """
    Custom user manager (MemberManager) where the unique identifier is the email.
    """
    def create_user(self, email, password, phone=None, **extra_fields):
        if not email:
            raise ValueError("The Email must be set for a Member.")
        email = self.normalize_email(email)
        user = self.model(email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, password, phone=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser is_staff must be True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser is_superuser must be True")
        return self.create_user(email, password, phone=phone, **extra_fields)



class Member(AbstractBaseUser, PermissionsMixin) :
    email = models.EmailField(("email address"), unique=True)
    password = models.CharField(max_length=255)
    joined_date = models.DateField(auto_now_add=True)
    phone = models.CharField(max_length=20, null=True)
    status = models.BooleanField(default=False)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS=[]

    objects=MemberManager()

    def __str__(self):
        return f"{self.email}"
    
class Address(models.Model):
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='addresses')

    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state_province = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.street_address}|{self.city}|{self.state_province}|{self.postal_code}|{self.country}"
    

class Profile(models.Model):
    user = models.OneToOneField(Member, on_delete=models.CASCADE)

    business_name = models.CharField(max_length=200, default="")
    

    contact_number = models.CharField(max_length=20, default="")

    emails = ArrayField(models.CharField(max_length=100), default=list)

    intent = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.user.email

class UploadedFile(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    original_name = models.CharField(max_length=255)
    gcs_path = models.CharField(max_length=1024)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def gcs_signed_url(self):
        try:
            credentials, project_id = google.auth.default()
            
            # Perform a refresh request to get the access token of the current credentials (Else, it's None)
            from google.auth.transport import requests
            r = requests.Request()
            credentials.refresh(r)

            print("CREDENTIALS TYPE:", type(credentials))
            print("SERVICE ACCOUNT EMAIL:", getattr(credentials, 'service_account_email', None))

            res = f'''
                CREDENTIALS TYPE:{type(credentials)}
                SERVICE ACCOUNT EMAIL: {getattr(credentials, 'service_account_email', None)}
                '''

            # Figure out which service account to use
            if hasattr(credentials, "service_account_email"):
                service_account_email = credentials.service_account_email
            else:
                # fallback: put your SA email here for dev, or raise error
                service_account_email = "634639548921-compute@developer.gserviceaccount.com"

            bucket_name = 'dubdebt-bucket'
            project_id = settings.GCP_PROJECT
            storage_client = storage.Client(project=project_id)
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(self.gcs_path)
            url = blob.generate_signed_url(
                version="v2",
                expiration=600,
                service_account_email=service_account_email,
                method="GET",
                response_disposition=f'attachment; filename="{self.original_name}"'
            )
            return res
        except Exception as e:
            return f"Error: {str(e)}"


    def __str__(self):
        return f"{self.user} - {self.original_name}"
