from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.conf import settings
import json
import stripe
from .models import Debtor, Debt

stripe.api_key = settings.STRIPE_SECRET_KEY


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

def payment(request, code):
    debt = get_object_or_404(Debt, unique_code=code)
    context = {
        'debt': debt
    }
    return render(request, 'payment.html', context)

def pay_debt(request, code):
    debt = get_object_or_404(Debt, unique_code=code)
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': f'Debt #{debt.unique_code}',
                    'description': debt.description or '',
                },
                'unit_amount': int((debt.amount + debt.interest) * 100),  # Stripe expects cents!
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri('/payment-success/') + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri('/payment-cancelled/'),
        metadata={'debt_id': debt.unique_code},
    )
    return redirect(session.url)

@csrf_exempt
def stripe_webhook(request):
    print("THIS IS HIT")
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        debt_code = session['metadata'].get('debt_id')
        Debt.objects.filter(unique_code=debt_code).update(is_settled=True)
        print("Settled the debt", debt_code)


    return HttpResponse(status=200)

@csrf_exempt
def sms_send_view(request):
    data = json.loads(request.body)
    debtor_id = data['debtor_id']
    message_type = data['message_type']
    # Lookup debtor, construct message, send via Twilio, update ScheduledMessage status
    print(f"THIS IS A TASK QUERY TO SEND AN SMS OBJECT TO USER {debtor_id}")
