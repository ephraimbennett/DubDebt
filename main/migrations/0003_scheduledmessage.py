# Generated by Django 4.2.23 on 2025-07-17 15:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_creditor_debtor_unique_code_debt'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScheduledMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('send_time', models.DateTimeField()),
                ('task_name', models.CharField(max_length=255, unique=True)),
                ('message_type', models.CharField(max_length=50)),
                ('status', models.CharField(default='scheduled', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('debtor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.debtor')),
            ],
        ),
    ]
