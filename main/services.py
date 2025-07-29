from google.cloud import tasks_v2
from django.conf import settings

import json

import os
from twilio.rest import Client

from .models import ScheduledMessage

def schedule_sms_task(debtor_id, debt_id, send_time, message_type):
    client = tasks_v2.CloudTasksClient()
    project = settings.GCP_PROJECT
    queue = 'sms-targeting'
    location = settings.GCP_REGION
    url = 'https://dubdebt.com/main/api/sms/send/'

    # Unique task name
    task_name = f"debtor-{debtor_id}-{message_type}-{send_time.strftime('%Y%m%d%H%M%S')}"
    parent = client.queue_path(project, location, queue)
    task = {
        'name': f"{parent}/tasks/{task_name}",
        'http_request': {
            'http_method': tasks_v2.HttpMethod.POST,
            'url': url,
            'headers': {'Content-type': 'application/json'},
            'body': json.dumps({
                'debtor_id': debtor_id,
                'debt_id': debt_id,
                'message_type': message_type,
            }).encode(),
        },
        'schedule_time': send_time,
    }
    client.create_task(request={'parent': parent, 'task': task})
    return task_name


def cancel_scheduled_tasks(debt):
    client = tasks_v2.CloudTasksClient()
    project = settings.GCP_PROJECT
    queue = 'sms-targeting'
    location = settings.GCP_REGION
    parent = client.queue_path(project, location, queue)
    messages = ScheduledMessage.objects.filter(debt=debt, status="scheduled")
    for msg in messages:
        task_path = task_path = client.task_path(project, location, queue, msg.task_name)
        print(task_path)
        try:
            client.delete_task(name=task_path)
            msg.status = "cancelled"
            msg.save()
        except Exception as e:
            # Task might already have run or not exist; handle/log gracefully
            print(e)
            pass



def send_sms_via_twilio(to_number, message_body):
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    from_number = os.environ['TWILIO_PHONE_NUMBER']

    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=message_body,
        from_=from_number,
        to=to_number
    )
    return message.sid  # Or handle/log as needed
