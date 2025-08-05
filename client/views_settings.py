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
from .models import Member, Profile, Address, WithdrawalSettings
from main.models import Creditor, Debt, Debtor

def settings(request):
    context = {}

    context.update(getPortalContext(request))
    return render(request, "portal_settings.html", context)

@login_required
def method_data(request):
    withdrawals, created = WithdrawalSettings.objects.get_or_create(creditor=request.user.profile.creditor)

    res = [
        {
            'key': 'stripe',
            'connected': withdrawals.is_stripe_connected
        },
        {
            'key': 'ach',
            'connected': withdrawals.is_ach_connected
        },
        {
            'key': 'paypal',
            'connected': withdrawals.is_ach_connected
        }
    ]

    return JsonResponse(res, safe=False)

def stripe_account_link(request):
    if request.method != 'POST':
        return HttpResponseBadRequest("Only POST allowed.") 
    
    withdrawal_settings, created = WithdrawalSettings.objects.get_or_create(creditor=request.user.profile.creditor)

    if not withdrawal_settings.is_stripe_connected:
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


        withdrawal_settings.is_stripe_connected = True
        withdrawal_settings.stripe_connect_id = account.id
        withdrawal_settings.save()

        return JsonResponse({'url': account_link.url})
    else:
        if len(withdrawal_settings.login_link) == 0:
            login_link = stripe.Account.create_login_link(
                withdrawal_settings.stripe_connect_id
            )
            withdrawal_settings.login_link = login_link.url
            return JsonResponse({'url': login_link.url})
            
        else:
            return JsonResponse({'url': withdrawal_settings.login_link})



def getPortalContext(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    return {
        'plan': "Per Recovery",
        'dubscore': 100,
        'business_name': profile.business_name,
        'user': user
    }