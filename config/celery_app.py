import os

from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("wuxiaworld")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
app.conf.beat_schedule = {
    'reset_weekly': {
        'task': 'wuxiaworld.novels.tasks.reset_weekly_views',
        'schedule': crontab(hour=0, minute=0,day_of_week = 0),
    },
    'reset_monthly': {
        'task': 'wuxiaworld.novels.tasks.reset_monthly_views',
        'schedule': crontab(hour=0, minute=0,day_of_month = 1),
    },
    'reset_yearly': {
        'task': 'wuxiaworld.novels.tasks.reset_yearly_views',
        'schedule': crontab(hour=0, minute=0,day_of_week = 0, month_of_year = 1),
    },

    'filter_chapter_text': {
        'task': 'wuxiaworld.scraper.tasks.filter_blacklist_patterns',
        'schedule': crontab(hour=0, minute=0),
    },
    'increment_views': {
        'task': 'wuxiaworld.novels.tasks.add_views',
        'schedule': 60*5,
    }
}