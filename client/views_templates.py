from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed

from .models import Profile
from main.models import MessageTemplate, CustomSMSTemplate, MessageTemplateRouter, EmailTemplate

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

    # also grab the custom data if it exists
    message_types = ["initial", "followup1", "followup2"]
    sms_router, created = MessageTemplateRouter.objects.get_or_create(user=request.user.profile)
    custom_data = []
    for m in message_types:
        item = sms_router.get_template(m)
        custom_data.append({'title': item.title, 'template': item.template})

    context['templates'] = json.dumps(data)
    print(custom_data)
    context['custom_templates'] = json.dumps(custom_data)

    return render(request, "portal_templates.html", context)

@login_required
def etemplates(request):

    context = getPortalContext(request)

    # return default template stuff as JSON
    templates = EmailTemplate.objects.all()
    data = [{
        'title': t.type,
        'subject': t.subject,
        'template': t.body
    } for t in templates]

    # also grab the custom data if it exists
    message_types = ["initial", "followup1", "followup2"]
    email_router, created = MessageTemplateRouter.objects.get_or_create(user=request.user.profile)
    custom_data = []
    for m in message_types:
        item = email_router.get_email_template(m)
        custom_data.append({'title': item.type, 'template': item.body, 'subject': item.subject})

    context['templates'] = json.dumps(data)
    print(custom_data[0])
    context['custom_templates'] = json.dumps(custom_data)

    return render(request, "portal_etemplates.html", context)

def set_message_template(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            new_templates = data.get('new_templates')
            sms_router, created = MessageTemplateRouter.objects.get_or_create(user=request.user.profile)
            print(new_templates)
            # should be 
            sms_router.set_template(new_templates)
        except Exception as e:
            print(e)
            return HttpResponseBadRequest("Data was malformed.")
        else:
            return JsonResponse({'success': True})
    return HttpResponseNotAllowed("Wrong ")

def set_email_template(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            new_templates = data.get('new_templates')
            email_router, created = MessageTemplateRouter.objects.get_or_create(user=request.user.profile)

            email_router.set_email_template(new_templates)
        except Exception as e:
            print(e)
            return HttpResponseBadRequest("Data was malformed.")
        else:
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