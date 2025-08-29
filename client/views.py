from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .views_debtor import debtor_get, debtor_post
from .forms import ContactForm

import json


from .forms import MemberCreationForm
from .models import Member, Profile, Address
from main.models import Creditor, Debt, Debtor

# Create your views here.
def clients(request):
    return render(request, "clients.html")

def login_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('/portal-dashboard/')
        else:
            return render(request, "login.html", {
                'error' : "Invalid email or password.",
                'email': email
            })
    else:
        return render(request, "login.html")
    
def signup(request):
    if request.method == 'POST':
        form = MemberCreationForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            form.save()
            user = authenticate(request, email=form.cleaned_data['email'], password=form.cleaned_data['password1'])
            login(request, user)
            return redirect('/profile-edit/')
        else:
            errors = {}
            return render(request, 'signup.html', {
                'errors': form.errors.as_text(),
                'email': request.POST.get('email')
            })

    return render(request, "signup.html")

def privacy(request):
    return render(request, "privacy.html")

def terms(request):
    return render(request, "terms.html")

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():

            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            # Send an email
            send_mail(
                f'From {name}, Subject: {subject}',
                f'Email: {email} Message: {message}',
                settings.EMAIL_HOST_USER,  # From email
                ['team@dubdebt.com'],  # To email
                fail_silently=False,
            )


            # Process the form data
            return render(request, 'contact.html', {'form': form, 'success': True})
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form, 'success': False})


@login_required
def portal(request):

    context = getPortalContext(request)
    return render(request, "portal_base.html", context)

@login_required
def portal_debtors(request):

    if request.method == 'GET':
        return debtor_get(request)
    elif request.method == 'POST':
        return debtor_post(request)
    

@login_required
def profile_edit(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    adresses_o = profile.addresses.all()
    
    if (request.method == 'POST'):
        profile.business_name = request.POST.get('business_name')
        profile.contact_number = request.POST.get('contact_number')
        profile.intent = request.POST.get('intent')
        emails = request.POST.getlist('emails')
        print(request.POST)
        print(emails)
        profile.emails = [emails] if isinstance(emails, str) else emails

        # add a creditor object
        creditor = profile.creditor
        if creditor is None:
            new = Creditor(name=profile.business_name, collected=0.0)
            new.save()
            profile.creditor = new
        else:
            creditor.name = profile.business_name
            creditor.save()

        profile.save()
        
        if isinstance(request.POST.get('addresses'), str):
            if is_new_address(request.POST.get('addresses'), adresses_o):
                a = make_address(request.POST.get('addresses'), profile)
                a.save()
        else:
            addresses = []
            if request.POST.get('addresses') is not None:
                for address in request.POST.get('addresses'):
                    if is_new_address(address, adresses_o):
                        a = make_address(address, profile)
                        address.append(a)
                Address.objects.bulk_create(addresses)
    context = {
        'profile': profile,
        'addresses': adresses_o,
        'emails': profile.emails
    }
    context.update(getPortalContext(request))
    return render(request, "profile_edit.html", context)

def getPortalContext(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    return {
        'plan': "Per Recovery",
        'dubscore': 100,
        'business_name': profile.business_name,
        'user': user
    }

def is_new_address(a, current):
    for c in current:
        print(a.strip(), str(c).strip())
        if a.strip() == str(c):
            return False
    return True

def is_new_creditor(name, current):
    if name == current.name:
        return False
        
    return True

def make_address(line, profile):
    items = line.split('|')
    a = Address(profile=profile)
    a.street_address = items[0]
    a.city = items[1]
    a.state_province = items[2]
    a.postal_code = items[3]
    a.country = items[4]
    return a

from google.oauth2 import id_token
from google.auth.transport import requests

@csrf_exempt
def auth_receiver(request):
    """
    Google calls this URL after the user has signed in with their Google account.
    """
    print('Inside')
    token = request.POST['credential']
 
    try:
        user_data = id_token.verify_oauth2_token(
            token, requests.Request(), settings.GOOGLE_OAUTH_CLIENT_ID
        )
    except ValueError:
        return HttpResponse(status=403)
 
    # In a real app, I'd also save any new user here to the database.
    # You could also authenticate the user here using the details from Google 
    # (https://docs.djangoproject.com/en/4.2/topics/auth/default/#how-to-log-a-user-in)
    email = user_data.get("email")
    User = get_user_model()
    user, created = User.objects.get_or_create(email=email, defaults={
        "email" : email
    })
    login(request, user)

    if created:
        return redirect('/profile-edit/')
 
    return redirect('portal-dashboard')
# comment