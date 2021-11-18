from django.db.models.signals import post_delete, pre_save,post_save, post_delete
from django.dispatch import receiver
from django.apps import apps
from django.utils.text import slugify
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialAccount
import json
from wuxiaworld.scraper.tasks import continous_scrape

#If Novel has a scrape link, start the initial scrape of the novel and create
# a periodic task to scrape every x interval.
def create_periodic_task(instance):
    if instance.repeatScrape:
        schedule, _ = IntervalSchedule.objects.get_or_create(
                    every = 3,
                    period = IntervalSchedule.HOURS
                    )
        task, _ = PeriodicTask.objects.get_or_create(
        interval=schedule, 
        name=instance.name,
        task='wuxiaworld.scraper.tasks.continous_scrape',
        args = json.dumps([instance.slug]),
        )

@receiver(post_delete, sender="novels.Profile")
def create_profile(sender, instance, created, **kwargs):
    settings = instance.settings
    if settings:
        settings.delete()
     
@receiver(post_delete, sender="novels.Novel")
def clear_views(sender,instance, **kwargs):
    novelView = instance.viewsNovelName
    if novelView:
        novelView.delete()
    novelTask = PeriodicTask.objects.filter(name = instance.name)
    if novelTask:
        novelTask.delete()
    
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
        create_periodic_task(instance)

@receiver(post_save, sender=SocialAccount)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile = apps.get_model('novels','Profile')
        Settings = apps.get_model('novels','Settings')
        newSettings = Settings.objects.create()
        profile = Profile.objects.create(user=instance.user, imageUrl = instance.get_avatar_url(),
                            settings = newSettings)

