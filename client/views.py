from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize


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
            return redirect('/profile-edit/')
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

@login_required
def portal(request):

    context = getPortalContext(request)
    return render(request, "portal_base.html", context)

@login_required
def portal_debtors(request):
    profile = Profile.objects.get(user=request.user)
    creditors = profile.creditors.all()
    debts_json = ""
    debts = []
    for creditor in creditors:
        debts.extend(list(creditor.debts.all()))

    debts_json = serialize('json', creditor.debts.all())

    debtors = []
    for debt in debts:
        #print(type(debt.debtor)) -- this line confirmed debt.debtor is a <class 'main.models.Debtor'>
        #debtors_json += (serialize('json', [debt.debtor])) # this line fails
        debtors.append(debt.debtor)
    
    debtors_json = serialize('json', debtors)
    print(debtors_json)

    context = {
        'debts_json': debts_json,
        'debtors_json': debtors_json
    }

    context.update(getPortalContext(request))

    return render(request, "portal_debtors.html", context)

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
        creditors = profile.creditors.all()
        if is_new_creditor(profile.business_name, creditors):
            creditor = Creditor(profile= profile, name=profile.business_name, collected=0.0)
            creditor.save()

        profile.save()
        
        if isinstance(request.POST.get('addresses'), str):
            if is_new_address(request.POST.get('addresses'), adresses_o):
                a = make_address(request.POST.get('addresses'), profile)
                a.save()
        else:
            addresses = []
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
        'amount_collected': 10.0,
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
    for c in current:
        if name == c.name:
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