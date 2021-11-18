from celery import shared_task
from django.apps import apps
import requests 
from django.utils.text import slugify
import json
from os import listdir
from .utils import *
import traceback
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from django.conf import settings
from django.db.models import Value, F, Func
from django.db import models 
import re
from wuxiaworld.scraper.utils.create_scraper import create_scraper
import concurrent.futures
import urllib3

def stop_repeat_scrape(novelObject) -> None:
    novelObject.repeatScrape = False
    novelObject.save()

def add_chapter(chapter, queriedNovel):
    Chapter = apps.get_model('novels', 'Chapter')
    BlacklistPattern = apps.get_model('novels', 'BlacklistPattern')
    listOfPatterns = BlacklistPattern.objects.filter(enabled = True, replacement = "").values_list(
        'pattern', flat=True
    )
    patternText = "|".join(listOfPatterns)
    chapterText = re.sub("<p>|<strong>|</strong>", "",chapter['body'] )
    chapterText = re.sub("</p>", "\n",chapterText)

    chapterText = re.sub(patternText, "",chapterText)
    patternsWithReplacement = BlacklistPattern.objects.filter(enabled = True).exclude(replacement = "")
        
    for pat in patternsWithReplacement:
        pattern = fr'{pat.pattern}'
        replacement = fr"{pat.replacement}"
        chapterText = re.sub(pattern, replacement,chapterText )
        

    _, chapter = Chapter.objects.get_or_create(index = chapter['chapter']['id'],
                novelParent = queriedNovel, defaults={
                'text':chapterText,'title':chapter['chapter']['title'],
                'scrapeLink':chapter['chapter']['url']
            })

def perform_scrape(scrapeLink, queriedNovel):
    scraper = create_scraper(scrapeLink)
    Chapter = apps.get_model("novels", "Chapter")
    novel_chapters = Chapter.objects.filter(novelParent = queriedNovel)
    index = 0
    if novel_chapters.count():
        lastChapter  = novel_chapters.last()
        index = lastChapter.index
        if novel_chapters.count() >= len(scraper.chapters):
            return
    toScrape = {}
    for x in scraper.chapters:
        if settings.DEBUG and int(x['id']) > index + 5:
            break
        if int(x['id']) < index:
            continue
        else:
            print("should be working")
            toScrape[scraper.executor.submit(scraper.download_chapter_body, x)] = {'id':x['id'],
             'title':x['title'], 'url':x['url']}
    
    for future in concurrent.futures.as_completed(toScrape):
        chapter = toScrape[future]

        try:
            temp_result = future.result(timeout = 5)
            if temp_result:
                result = {'body':temp_result,'chapter':{'id':chapter['id'],'title':chapter['title'],
                'url':chapter['url'] } }
                add_chapter(result,queriedNovel)

        except (TypeError, requests.exceptions.SSLError,
            urllib3.exceptions.MaxRetryError, requests.exceptions.ConnectionError,
            urllib3.exceptions.NewConnectionError, requests.exceptions.MissingSchema,
            AttributeError,requests.exceptions.ReadTimeout ):
            pass
    if scraper:
        scraper.destroy()
    resultData = {'data':f"{len(toScrape)} chapters downloaded for {queriedNovel.name}"}
    return resultData

@shared_task
def continous_scrape(slug):
    Novel = apps.get_model("novels", "Novel")
    Source = apps.get_model("scraper", "Source")
    queriedNovel = Novel.objects.get(slug = slug)
    sources = Source.objects.filter(source_novel__slug = slug).order_by("-priority")
    if not sources.count():
        return f"No Sources for {queriedNovel.name}"
    if not queriedNovel.repeatScrape:
        return f"Scraper not turned on for {queriedNovel.name}"
    resultData = {}
    for source in sources:

        try:
            resultData = perform_scrape(source.url, queriedNovel)
            break
        except Exception as e:
            print(traceback.format_exc())
            continue
    
    return resultData

@shared_task
def filter_blacklist_patterns():
    Chapter = apps.get_model('novels', 'Chapter')
    BlacklistPattern = apps.get_model('novels', 'BlacklistPattern')

    listOfPatterns = BlacklistPattern.objects.filter(enabled = True, replacement = "").values_list(
        'pattern', flat=True
    )
    patternText = "|".join(listOfPatterns)
    pattern = Value(fr'{patternText}')
    replacement = Value(r'') 
    flags = Value('g')
    Chapter.objects.update(
        text=Func(
            models.F('text'),
            pattern, replacement, flags,
            function='REGEXP_REPLACE',
            output_field=models.TextField(),
        )
    )

    patternsWithReplacement = BlacklistPattern.objects.filter(enabled = True).exclude(replacement = "")
        
    for pat in patternsWithReplacement:
        pattern = Value(fr'{pat.pattern}')
        replacement = Value(fr"{pat.replacement}")
        Chapter.objects.update(
        text= Func(
            models.F('text'),
            pattern, replacement, flags,
            function='REGEXP_REPLACE',
            output_field=models.TextField(),
        )
        )
