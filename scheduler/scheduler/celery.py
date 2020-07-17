from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings
# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scheduler.settings')
app = Celery('scheduler')
# Celery will apply all configuration keys with defined namespace
app.config_from_object('django.conf:settings', namespace='CELERY')
# Load tasks from all registered apps
app.autodiscover_tasks()
