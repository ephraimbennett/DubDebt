from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from django.shortcuts import get_object_or_404


from django.core.serializers import serialize

import json

from .models import Member, Profile, Address
from main.models import Creditor, Debt, Debtor, Payment

@login_required
def payments(request):
    context = {}
    context.update(getPortalContext(request))
    return render(request, "portal_payments.html", context)

@login_required
def api_payments(request):
    # Grab the all payments that are associated with this
    # Also, preselects the debts and debtors by joining the tables
    payments = Payment.objects.select_related('debt__debtor').filter(debt__creditor_name=request.user.profile.creditor)
    debts = Debt.objects.select_related('debtor').filter(creditor_name=request.user.profile.creditor)
    
    payments_data = [{
        'title': str(payment),
        'id': payment.id,
        'date': payment.date.isoformat(),
        'in_full': payment.in_full,
        'method': payment.method,
        'debt_code': payment.debt.unique_code,
        'debt_id': payment.debt.id,
        'debt_amount': payment.debt.amount,
        'debt_interest': payment.debt.interest,
        'debtor_code': payment.debt.debtor.unique_code,
        'debtor_name': str(payment.debt.debtor), 
        'debtor_phone': payment.debt.debtor.phone
    } for payment in payments]
    debts_data = [{
        'debt_code': debt.unique_code,
        'debt_id': debt.id,
        'debt_amount': debt.amount,
        'debt_interest': debt.interest,
        'debtor_code': debt.debtor.unique_code,
        'debtor_name': str(debt.debtor), 
        'debtor_phone': debt.debtor.phone
    } for debt in debts]
    final_data = [payments_data, debts_data]

    return JsonResponse(final_data, safe=False)

def api_add_payment(request):
    if request.method != 'POST':
        return HttpResponseBadRequest(405)

    data = json.loads(request.body)
    debt = get_object_or_404(Debt, unique_code=data['debt_code'])

    if (hasattr(debt, 'payment')) and (debt.payment.in_full):
        return JsonResponse({
            'success': False,
            'message': 'The payment already exists'
        })
    print(data)
    
    Payment.objects.create(debt=debt, amount=data['amount'], date=data['date'], method=data['method'])

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