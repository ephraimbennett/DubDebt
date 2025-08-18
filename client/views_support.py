from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.mail import send_mail


from uuid import uuid4

from main.services import schedule_sms_task
from main.models import ScheduledMessage

from .models import UploadedFile, Profile, Issue, MeetingRequest

from datetime import datetime, timedelta

from google.cloud import storage

import json


def support(request):
    context = {}

    context.update(getPortalContext(request))

    return render(request, "portal_support.html", context)

def raise_issue(request):

    data = json.loads(request.body)

    try:
        Issue.objects.create(
            title=data['title'], priority=data['priority'], description=data['description'], user=request.user.profile)
    except Exception as e:
        print(e)
        return JsonResponse({'success': False})

    return JsonResponse({'success': True})

def request_meeting(request):
    data = json.loads(request.body)

    try:

        MeetingRequest.objects.create(
            reason = data['reason'],
            date_time = data['datetime'],
            method = data['method'],
            user = request.user.profile
        )

        # Send an email
        send_mail(
            f'Meeting request from {request.user}',
            f"Date/Time: {data['datetime']} \n Method: {data['method']}. \n Reason: {data['reason']}",
            settings.EMAIL_HOST_USER,  # From email
            ['team@dubdebt.com'],  # To email
            fail_silently=False,
        )
    except Exception as e:
        print(e)
        return JsonResponse({'success': False})

    print(data)

    return JsonResponse({'success': True})

def getPortalContext(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    return {
        'plan': "Per Recovery",
        'dubscore': 100,
        'business_name': profile.business_name,
        'user': user
    }