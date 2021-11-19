from django.db.models.signals import post_delete, pre_save,post_save, post_delete
from django.dispatch import receiver
from django.apps import apps
from django.utils.text import slugify
from wuxiaworld.scraper.tasks import continous_scrape

@receiver(post_delete, sender="scraper.Source")
def remove_chapters(sender, instance, **kwargs):
    Chapter = apps.get_model('novels', "Chapter")
    chapters_downloaded = Chapter.objects.filter(novelParent = instance.source_novel)
    chapters_with_source = chapters_downloaded.filter(scrapeLink__icontains = instance.base_url).count()
    if chapters_with_source:
        chapters_downloaded.delete()

     