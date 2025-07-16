from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


from .forms import MemberCreationForm
from .models import Member, Profile

# Create your views here.
def clients(request):
    return render(request, "clients.html")

def login_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email, password)
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
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
            return redirect('/')
        else:
            errors = {}
            return render(request, 'signup.html', {
                'errors': form.errors.as_text(),
                'email': request.POST.get('email')
            })

    return render(request, "signup.html")

@login_required
def profile_edit(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    context = {
        'profile': profile,
        'addresses': profile.addresses.all()
    }
    return render(request, "profile_edit.html", context)