from __future__ import absolute_import 
import os
from celery import Celery

#set the default Django module for the "clery" programm
os.environ.setdefault('DJANGO_SETTINGS_MODULE','youtube2youku.settings')
from django.conf import settings

app = Celery('youtube2youku')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
