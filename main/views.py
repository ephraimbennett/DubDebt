from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
import json
from .models import Debtor

# Create your views here.

def home(request):
    return render(request, "landing.html")

def verify(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        code = data.get('code')
        if code:
            exists = Debtor.objects.filter(unique_code=code).exists()
            print("All codes:", list(Debtor.objects.values_list('unique_code', flat=True)))
            print(code)
            request.session['code'] = code
            return JsonResponse({'success': exists})
    return render(request, "verify.html")  

def balance(request):

    debtor = get_object_or_404(Debtor, unique_code=request.session['code'])
    debts = debtor.debts.all()

    for debt in debts:
        debt.creditor = str(debt.creditor_name)

    total = sum((debt.amount + debt.interest) for debt in debts)
    user = {
        'name': str(debtor),
        'balance': total
    }
    context={
        'user': user,
        'debts': debts
    }
    return render(request, "balance.html", context)