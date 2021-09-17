from django.db.models.signals import post_delete, pre_save,post_save
from django.dispatch import receiver
from django.apps import apps
from django.utils.text import slugify
from .tasks import initial_scrape
from django_celery_beat.models import CrontabSchedule, PeriodicTask
import pytz
import json
from datetime import datetime,timedelta

@receiver(post_delete, sender="novels.Novel")
def clear_views(sender,instance, **kwargs):
    novelView = instance.viewsNovelName
    if novelView:
        novelView.delete()
    
@receiver(pre_save,sender = "novels.Novel")
def novel_check(sender,instance,**kwargs):
    
    if not instance.slug:
        newSlug = slugify(instance.name)
        instance.slug = newSlug
    if not instance.viewsNovelName:
        NovelViews = apps.get_model('novels','NovelViews')
        novelView, _ = NovelViews.objects.get_or_create(viewsNovelName = instance.slug)
        instance.viewsNovelName = novelView

    if not instance.category:
        Category = apps.get_model('novels','Category')
        noneCategory, _ = Category.objects.get_or_create(name = "None", slug = "none")
        instance.category = noneCategory

    
@receiver(post_save,sender = "novels.Novel")
def init_scrape(sender,instance,**kwargs):
    if kwargs['created']:
        if instance.scrapeLink:
            initial_scrape.delay(instance.scrapeLink)
            if instance.repeatScrape:
                schedule, _ = CrontabSchedule.objects.get_or_create(
                    minute='47',
                    hour='*',
                    day_of_week='*',
                    day_of_month='*',
                    month_of_year='*',
                    timezone=pytz.timezone('Canada/Pacific')
                    )
                task, _ = PeriodicTask.objects.get_or_create(crontab=schedule,
                    name=f'{instance.name} - Continious',
                    task='wuxiaworld.novels.tasks.continous_scrape',
                    args = json.dumps([instance.scrapeLink,]),
                    )

