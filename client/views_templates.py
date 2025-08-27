from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.http import JsonResponse, HttpResponseBadRequest

from .models import Profile
from main.models import MessageTemplate

import json


@login_required
def templates(request):

    context = getPortalContext(request)

    # return default template stuff as JSON
    templates = MessageTemplate.objects.all()
    data = [{
        'title': t.title,
        'template': t.template
    } for t in templates]

    context['templates'] = json.dumps(data)

    return render(request, "portal_templates.html", context)


def getPortalContext(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    return {
        'plan': "Per Recovery",
        'dubscore': 100,
        'business_name': profile.business_name,
        'user': user
    }