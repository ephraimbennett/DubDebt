from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.http import JsonResponse



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
    context = {
        'debts_json': debts_json,
        'debtors_json': debtors_json
    }

    context.update(getPortalContext(request))

    return render(request, "portal_debtors.html", context)

def debtor_post(request):
    data = json.loads(request.body)
    print(data.get('unique_code'))
    try:
        debtor = Debtor.objects.get(unique_code=data.get('unique_code'))

        debtor.first_name = data.get('first_name')
        debtor.last_name = data.get('last_name')

        debtor.phone = data.get('phone')
        debtor.email = data.get('email')
        
        debtor.save()
        result = {
            'success': True
        }
    except Exception as e:
        print("H*UUUHUH")
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