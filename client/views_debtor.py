from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.http import JsonResponse

from main.services import schedule_sms_task
from main.models import ScheduledMessage

from datetime import datetime, timedelta

import json


from .forms import MemberCreationForm
from .models import Member, Profile, Address
from main.models import Creditor, Debt, Debtor



def debtor_get(request):
    profile = Profile.objects.get(user=request.user)
    creditors = profile.creditors.all()
    debts_json = ""
    debts = []
    for creditor in creditors:
        debts.extend(list(creditor.debts.all()))

    debts_json = serialize('json', creditor.debts.all())

    debtors = []
    for debt in debts:
        debtors.append(debt.debtor)
    
    debtors_json = serialize('json', debtors)
   
    if (request.GET.get('data-only')):
        context = {
            'debts_json': json.loads(debts_json),
            'debtors_json': json.loads(debtors_json)
        }
        return JsonResponse(context)

    context = {
        'debts_json': debts_json,
        'debtors_json': debtors_json
    }

    context.update(getPortalContext(request))

    return render(request, "portal_debtors.html", context)


def debtor_post(request):
    data = json.loads(request.body)
    if data.get('unique_code') is None:

        phone = data.get('phone')
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        debtor, created = Debtor.objects.get_or_create(first_name=first_name, last_name=last_name,
                                                       phone=phone)
        print(created)
    else:
        try:
            debtor = Debtor.objects.get(unique_code=data.get('unique_code'))
        except Exception as e:
            print(e)
    try:
        
        debtor.first_name = data.get('first_name')
        debtor.last_name = data.get('last_name')

        debtor.phone = data.get('phone')
        debtor.email = data.get('email')
        
        debtor.save()

        if data.get("unique_code") is None:
            # grab creditors for below
            profile = Profile.objects.get(user=request.user)
            creditors = profile.creditors.all()
            # add a default debt - can edit / remove 
            debt = Debt()
            debt.debtor = debtor
            debt.creditor_name = creditors.first()
            debt.amount = 0.0
            debt.interest = 0.0
            debt.incur_date = "2000-01-01"
            debt.due_date = "2000-01-01"
            debt.description = "DEFAULT"
            debt.save()
        result = {
            'success': True
        }
    except Exception as e:
        print(e)
        result = {
            'success': False
        }

    return JsonResponse(result)

def debt_edit(request):
    data = json.loads(request.body)
    print(data)
    try:
        if data.get("unique_code") is None:
            # grab creditors for below
            profile = Profile.objects.get(user=request.user)
            creditors = profile.creditors.all()
            debt = Debt()
            debt.creditor_name = creditors.first()
            debt.debtor = Debtor.objects.get(unique_code=data.get('debtor'))
        else:
            debt = Debt.objects.get(unique_code=data.get('unique_code'))
        debt.amount = 0.0 if len(data['amount']) == 0 else float(data['amount'])
        debt.interest = 0.0 if len(data['interest']) == 0 else float(data['interest'])
        debt.incur_date = "2000-01-01" if len(data['incur_date']) == 0 else data['incur_date']
        debt.due_date = "2000-01-01" if len(data['due_date']) == 0 else data['due_date']
        debt.description = data['description']
        
        debt.save()
        result = {
            'success': True
        }
    except Exception as e:
        print(e)
        result = {
            'success': False
        }
    return JsonResponse(result)


reminder_schedule = [
    (0, "initial"),      # immediate
    (2, "followup1"),    # 2 days later
    (7, "followup2"),    # 7 days after start
]

def debt_collect(request):
    data = json.loads(request.body)
    print(data)
    start_date = datetime.now()
    try:
        debt = Debt.objects.get(unique_code=data.get('unique_code'))
        for offset_days, message_type in reminder_schedule:
            send_time = start_date + timedelta(days=offset_days)
            task_name = schedule_sms_task(debt.debtor.id, debt.id, send_time, message_type)
            ScheduledMessage.objects.create(
                debtor=debt.debtor,
                send_time=send_time,
                task_name=task_name,
                message_type=message_type,
                status="scheduled",
            )
        debt.collecting = True
        debt.save()
        result = {
            'success': True
        }
    except Exception as e:
        print(e)
        result = {
            'success': False
        }
    return JsonResponse(result)

def getPortalContext(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    return {
        'amount_collected': 10.0,
        'dubscore': 100,
        'business_name': profile.business_name,
        'user': user
    }