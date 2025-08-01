from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


from main.services import schedule_sms_task, cancel_scheduled_tasks
from main.models import ScheduledMessage, Creditor

from datetime import datetime, timedelta

import json

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

from .forms import MemberCreationForm
from .models import Member, Profile, Address
from main.models import Creditor, Debt, Debtor

def settings(request):
    context = {}

    context.update(getPortalContext(request))
    return render(request, "portal_settings.html", context)

def stripe_account_link(request):
    if request.method != 'POST':
        return HttpResponseBadRequest("Only POST allowed.") 
    
    account = stripe.Account.create(
        type="express",  # or "standard", usually "express" is best
        email=request.user.email,  # optional, but helps Stripe prefill
    )

    account_link = stripe.AccountLink.create(
        account = account.id,
        refresh_url = "http://localhost:8080/portal-settings/",
        return_url = "http://localhost:8080/portal-debtors/",
        type = "account_onboarding",
    )

    creditor = request.user.profile.creditor
    creditor.is_stripe_connected = True
    creditor.stripe_connect_id = account.id
    creditor.save()

    return JsonResponse({'url': account_link.url})



def getPortalContext(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    return {
        'plan': "Per Recovery",
        'dubscore': 100,
        'business_name': profile.business_name,
        'user': user
    }