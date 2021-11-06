from celery import shared_task
# from .models import Category, Author, Novel, Chapter,NovelViews
from django.apps import apps
from datetime import datetime, date, timedelta
import requests 
import pandas as pd
from django.utils.text import slugify
import json
from os import listdir
from celery.task import periodic_task 
from celery.schedules import crontab
import random
from .utils import *
from .sources.wuxiasite import WuxiaSiteCrawler
from .sources.readnovelfull import ReadNovelFullCrawler
from .sources.vipnovel import VipNovel
from .sources.wuxiaco import WuxiaCoCrawler

import os
import logging
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from django.conf import settings
from django.db.models.functions import Replace
from django.db.models import Value, F, Func
from django.db import models 

logger = logging.getLogger("sentry_sdk")

chapters_folder = "chapters"

def stop_repeat_scrape(novelObject):
    novelObject.repeatScrape = False
    novelObject.save()

def getNovelInfo(scrapeLink):
    Novel = apps.get_model('novels','Novel')

    queriedNovel = Novel.objects.get(scrapeLink = scrapeLink)
    if queriedNovel.sources == "WuxSite":
        scraper = WuxiaSiteCrawler()
    elif queriedNovel.sources == "ReadNovelFull":
        scraper = ReadNovelFullCrawler()
    elif queriedNovel.sources == "VipNovel":
        scraper = VipNovel()
    elif queriedNovel.sources == "WuxiaCo":
        scraper = WuxiaCoCrawler()
    scraper.novel_url = scrapeLink
    scraper.read_novel_info()
    
    return scraper

def add_chapter(chapter, queriedNovel):
    Chapter = apps.get_model('novels', 'Chapter')
    BlacklistPattern = apps.get_model('novels', 'BlacklistPattern')
    listOfPatterns = BlacklistPattern.objects.filter(enabled = True, replacement = "").values_list(
        'pattern', flat=True
    )
    patternText = "|".join(listOfPatterns)

    chapterText = re.sub(patternText, "",chapter['body'] )
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

@shared_task
def initial_scrape(scrapeLink) -> dict:
    Novel = apps.get_model("novels", "Novel")
    queriedNovel = Novel.objects.get(scrapeLink = scrapeLink)
    result = {}
    error = {}
    scraper = None
    try:
        scraper = getNovelInfo(scrapeLink)
        queriedNovel.novelRef = scraper.novel_id
        if settings.DEBUG:
            results = scraper.executor.map(scraper.download_chapter_body,scraper.chapters[:2])
        else:
            results = scraper.executor.map(scraper.download_chapter_body,scraper.chapters[:10])
        for result in results:
            add_chapter(result, queriedNovel)
        
        result = {'data':f"{len(scraper.chapters)} chapters downloaded for {queriedNovel.name}"}
        queriedNovel.repeatScrape = True
        queriedNovel.save()

    except requests.exceptions.SSLError as e:
        error = {'error':"SSL Error"}
        logger.error(f"Novel {queriedNovel.name} failed due to : Proxy error. Will restart later")
    
    except requests.exceptions.ConnectionError as e:
        error = {'error':"ConnectionError Error"}
        logger.error(f"Novel {queriedNovel.name} failed due to : Connection error. Will restart later")

    except Exception as e:
        error = {'error':f"{e}"}
        logger.error(f"Novel {queriedNovel.name} failed due to : {e}")
        stop_repeat_scrape(queriedNovel)

    schedule, _ = IntervalSchedule.objects.get_or_create(
                    every = 3,
                    period = IntervalSchedule.HOURS
                    )
    task, _ = PeriodicTask.objects.get_or_create(
        interval=schedule, 
        name=queriedNovel.name,
        task='wuxiaworld.novels.tasks.continous_scrape',
        args = json.dumps([queriedNovel.scrapeLink,]),
        )
    if scraper:
        scraper.destroy()
    return {'result':result,'error':error}

@shared_task
def continous_scrape(scrapeLink):
    Novel = apps.get_model("novels", "Novel")
    Chapter = apps.get_model("novels", "Chapter")
    queriedNovel = Novel.objects.get(scrapeLink = scrapeLink)
    scraper = None
    result = {}
    error = {}
    try:
        if not queriedNovel.repeatScrape:
            return True
        scraper = getNovelInfo(scrapeLink)
        if not queriedNovel.novelRef:
            queriedNovel.novelRef = scraper.novel_id
            queriedNovel.save()

        novel_chapters = Chapter.objects.filter(novelParent = queriedNovel)
        index = 0
        if novel_chapters.count():
            lastChapter  = novel_chapters.last()
            index = lastChapter.index
            if novel_chapters.count() >= len(scraper.chapters):
                return
        if settings.DEBUG:
            toScrape = [x for x in scraper.chapters if int(x['id']) > index][:3]
        else:
            toScrape = [x for x in scraper.chapters if int(x['id']) > index]
        results = scraper.executor.map(scraper.download_chapter_body,toScrape)
        for result in results:
            add_chapter(result,queriedNovel)
        result = {'data':f"{len(scraper.chapters)} chapters downloaded for {queriedNovel.name}"}
        
    except requests.exceptions.SSLError:
        error = {'error':"SSL Error"}
        logger.error(f"Novel {queriedNovel.name} failed due to : Proxy error. Will restart later")
    except requests.exceptions.ConnectionError :
        error = {'error':"Connection Error"}
        logger.error(f"Novel {queriedNovel.name} failed due to : Proxy error. Will restart later")
    except Exception as e:
        error = {'error':f"{e}"}
        logger.error(f"Novel {queriedNovel.name} failed due to : {e}")
        stop_repeat_scrape(queriedNovel)
    if scraper:
        scraper.destroy()
    return {'result':result,'error':error}
    
#Reset Views
@shared_task
def reset_weekly_views():
    NovelViews = apps.get_model('novels', 'NovelViews')
    novels = NovelViews.objects.all()
    novels.update(weeklyViews = 0)

@shared_task
def reset_monthly_views():
    NovelViews = apps.get_model('novels', 'NovelViews')
    novels = NovelViews.objects.all()
    novels.update(monthlyViews = 0)

@shared_task
def reset_yearly_views():
    NovelViews = apps.get_model('novels', 'NovelViews')
    novels = NovelViews.objects.all()
    novels.update(yearlyViews = 0)


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

@shared_task
def new_novel(x):
    Novel = apps.get_model('novels', 'Novel')
    Tag = apps.get_model('novels', 'Tag')
    Category = apps.get_model('novels', 'Category')
    Author = apps.get_model('novels', 'Author')

    novelInDb = Novel.objects.filter(slug = slugify(x['Book Name'])).count()
    if novelInDb > 0:
        return True
    try:
        tags = x['Book Tags'].split(",")
        tagsToPut = []
        for tag in tags:
            gotTag, _ = Tag.objects.get_or_create(name = tag)
            tagsToPut.append(gotTag)

        categories = x['Book Genre'].split(":")
        categoriesToPut = []  
        for category in categories:
            gotCategory, _ = Category.objects.get_or_create(name = category)
            categoriesToPut.append(gotCategory)
        try:
            author, _ = Author.objects.get_or_create(slug = slugify(x['Book Author']),
                                                    defaults = {'name' : x['Book Author']})
        except Exception as e:
            logger.error(f"Book {x['Book Name']} , author {x['Book Author']} already exists")
        
        if "wuxiaworld.site" in x['novelLink']:
            source = "WuxSite" 
        elif "vipnovel.com" in x['novelLink']:
            source = "VipNovel"
        elif ".novelfull.com" in x['novelLink']:
            source = "NovelFull"
        elif "wuxiaworld.co/" in x['novelLink']:
            source = "WuxiaCo"
        elif "readnovelfull.com" in x['novelLink']:
            source = "ReadNovelFull"
        else:
            source = ""
        novel, _ = Novel.objects.get_or_create(slug = slugify(x['Book Name']), author = author,
                defaults = {'slug': slugify(x['Book Name']), 'name' : x['Book Name'], 'image' : x['Book Image'], 'imageThumb' : x['thumbnail'],
                'linkNU' : x['Book URL'], 'description' : x['Description'], 'numOfChaps' : int(x['Book Chapters'].strip().split(" ")[0]),
                'numOfTranslatedChaps' : 0, 'novelStatus' : False , 'scrapeLink' : x['novelLink'], 'repeatScrape' : True,
                'sources':source})
        
        novel.category.set(categoriesToPut)
        novel.tag.set(tagsToPut)
        novel.save()
    except Exception as e:
        print(e)
@shared_task
def add_novels():
    sources = os.listdir('sources')
    for source in sources:
        df = pd.read_csv(f'sources/{source}').astype(str)
        df.applymap(lambda x: "" if len(x)>199 else x)
        for _ , x in df.iterrows():
            new_novel.delay(x.to_dict())
        
        


            

