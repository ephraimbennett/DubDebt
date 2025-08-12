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

from .models import UploadedFile, Profile

from datetime import datetime, timedelta

from google.cloud import storage

import json


def support(request):
    context = {}

    context.update(getPortalContext(request))

    return render(request, "portal_support.html", context)

def raise_issue(request):

    data = json.loads(request.body)

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