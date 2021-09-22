from django.apps import apps
from datetime import date
from celery import shared_task

@shared_task
def delete_dupes():
    
    Novel = apps.get_model('novels', 'Novel')
    Chapter = apps.get_model('novels','Chapter')
    today = date.today()
    novelQuery = Novel.objects.all()
    
    for novel in novelQuery:
        chapters = Chapter.objects.filter(novelParent = novel, dateAdded__gt = today).order_by("-dateAdded")
        for chap in chapters:
            check_dupe = Chapter.objects.filter(novelParent = novel, title = chap.title)
            if check_dupe.count()>1:
                chap.delete()
@shared_task
def delete_unordered_chapters():
    Novel = apps.get_model('novels', 'Novel')
    Chapter = apps.get_model('novels','Chapter')
    novelQuery = Novel.objects.all()
    print("unordered")
    for novel in novelQuery:
        chapters = Chapter.objects.filter(novelParent = novel).order_by("index")
        if chapters:
            firstChapter = chapters.first()
            if firstChapter.index>1:
                chapters.delete()