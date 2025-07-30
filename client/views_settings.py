from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


from main.services import schedule_sms_task, cancel_scheduled_tasks
from main.models import ScheduledMessage

from datetime import datetime, timedelta

import json


from .forms import MemberCreationForm
from .models import Member, Profile, Address
from main.models import Creditor, Debt, Debtor

def settings(request):
    context = {}

    context.update(getPortalContext(request))
    return render(request, "portal_settings.html", context)

def getPortalContext(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    return {
        'plan': "Per Recovery",
        'dubscore': 100,
        'business_name': profile.business_name,
        'user': user
    }