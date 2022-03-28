from celery import shared_task
from django.apps import apps
import requests 
from django.utils.text import slugify
import json
import traceback
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from django.conf import settings
from django.db import models 
from wuxiaworld.bug_reports.models import BugReport

@shared_task
def check_novels(slug):
    
