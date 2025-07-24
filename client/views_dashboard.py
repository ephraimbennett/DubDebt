from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from uuid import uuid4

from main.services import schedule_sms_task
from main.models import ScheduledMessage

from .models import UploadedFile

from datetime import datetime, timedelta

from google.cloud import storage

import json


from .forms import MemberCreationForm
from .models import Member, Profile, Address
from main.models import Creditor, Debt, Debtor

@login_required
def dashboard(request):
    context = {}

    if request.GET.get('data-only') == "y":
        # calculate the total amount collected
        profile = Profile.objects.get(user=request.user)
        creditors = profile.creditors.all()
        num_debts = len(creditors.first().debts.all())

        total_outstanding = 0
        total_collected = 0
        paid = 0
        collecting = 0
        for debt in creditors.first().debts.all():
            if debt.is_settled:
                total_collected += (debt.amount + debt.interest)
                paid += 1
            else:
                total_outstanding += (debt.amount + debt.interest)
            if debt.collecting:
                collecting += 1
        print(total_outstanding, total_collected)
        res = {
            'outstanding': total_outstanding,
            'collected': total_collected,
            'revenue_change': 201.2,
            'outstanding_change': 202.3,
            'repayment_rate': (paid / num_debts) * 100.0,
            'in_collection': collecting,
            'collecting_rate': (collecting / num_debts) * 100.0
        }
        return JsonResponse(res)
    else:
    
        context.update(getPortalContext(request))
        return render(request, "portal_dashboard.html", context)

@csrf_exempt 
def upload_file(request):
    if request.method != 'POST':
        return HttpResponseBadRequest("Only POST allowed.")
     
    file_obj = request.FILES.get('file')
    if not file_obj:
        return JsonResponse({'error': 'No file uploaded.'}, status=400)

    bucket_name = "dubdebt-bucket"
    destination_blob_name = f"uploads/{request.user.id}/{uuid4()}_{file_obj.name}"

    try:
        storage_client = storage.Client(project=settings.GCP_PROJECT)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_file(file_obj, content_type=file_obj.content_type)
    except Exception as e:
        print(e)
        return JsonResponse({'error': str(e)}, status=500)
    else:
        uploaded = UploadedFile()
        uploaded.user = Profile.objects.get(user=request.user)
        uploaded.original_name = file_obj.name
        uploaded.gcs_path = destination_blob_name
        uploaded.save()

    return JsonResponse({'message': 'Upload successful!', 'filename': file_obj.name})

def getPortalContext(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    return {
        'amount_collected': 10.0,
        'dubscore': 100,
        'business_name': profile.business_name,
        'user': user
    }