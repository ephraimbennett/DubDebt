from google.cloud import tasks_v2
from django.conf import settings

import json

from .models import ScheduledMessage

def schedule_sms_task(debtor_id, send_time, message_type):
    client = tasks_v2.CloudTasksClient()
    project = settings.GCP_PROJECT
    queue = 'sms-targeting'
    location = settings.GCP_REGION
    url = 'https://dubdebt.com/api/sms/send/'  # Update for your service

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
                'message_type': message_type,
            }).encode(),
        },
        'schedule_time': send_time,
    }
    client.create_task(request={'parent': parent, 'task': task})
    return task_name


def cancel_scheduled_tasks(debtor):
    client = tasks_v2.CloudTasksClient()
    project = settings.GCP_PROJECT
    queue = 'sms-reminders'
    location = settings.GCP_REGION
    parent = client.queue_path(project, location, queue)
    messages = ScheduledMessage.objects.filter(debtor=debtor, status="scheduled")
    for msg in messages:
        task_path = f"{parent}/tasks/{msg.task_name}"
        try:
            client.delete_task(name=task_path)
            msg.status = "cancelled"
            msg.save()
        except Exception as e:
            # Task might already have run or not exist; handle/log gracefully
            pass
