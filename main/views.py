from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.urls import reverse


import json
import stripe

from .models import Debtor, Debt, ScheduledMessage, MessageTemplate
from.services import send_sms_via_twilio


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

def balance(request, code):
    if request.session.get('code') is not None:
        debtor = get_object_or_404(Debtor, unique_code=request.session['code'])
    else:
        debtor = get_object_or_404(Debtor, unique_code=code)
        request.session['code'] = code
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
    print(request.path)
    return render(request, "balance.html", context)

def balance_redirect(request):
    if request.session.get('code') is not None:
        return redirect(reverse('balance_redirect') + request.session.get('code') + "/")
    else:
        return redirect(reverse("home"))

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
        success_url=request.build_absolute_uri(f'/main/payment-success/{code}/') + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri('/main/payment/' + code + '/'),
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
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)


    data = json.loads(request.body)
    debtor_id = data['debtor_id']
    debt_id = data['debt_id']
    message_type = data['message_type']

    print(debtor_id, debt_id, message_type)

    if not all([debtor_id, debt_id, message_type]):
        return JsonResponse({'error': 'Missing required parameters'}, status=400)

    debtor = Debtor.objects.get(pk=debtor_id)
    debt = Debt.objects.get(pk=debt_id)
    creditor = debt.creditor_name
    template_obj = MessageTemplate.objects.get(title=message_type)

    
    # Lookup debtor, construct message, send via Twilio, update ScheduledMessage status
    try:
        task = ScheduledMessage.objects.get(debtor=debtor, message_type=message_type)
    except ScheduledMessage.DoesNotExist:
        task = None
    except ScheduledMessage.MultipleObjectsReturned:
        # Handle case where multiple messages exist
        tasks = ScheduledMessage.objects.filter(
            debtor=debtor,
            message_type=message_type
        )
        task = tasks.first()

    
    
    body = template_obj.template
    body = body.format(name=f"{debtor.first_name}",
                       creditor=creditor.name,
                       amount=(debt.amount + debt.interest),
                       date = debt.incur_date,
                       url=f"{settings.BASE_URL}{reverse('payment', kwargs={'code': debt.unique_code})}")
    
    
    p = debtor.phone.replace("-", "")
    phone = f"+1{p}"

    send_sms_via_twilio(phone, body)

    task.status = "filled"
    task.save()

    return JsonResponse({"status": "ok"}, status=200)


def payment_success(request, code):
    debt = get_object_or_404(Debt, unique_code=code)
    debt.amount += debt.interest
    if not debt.is_settled:
        return redirect("/main/")
    context = {
        'debt': debt
    }
    return render(request, "payment_success.html", context)