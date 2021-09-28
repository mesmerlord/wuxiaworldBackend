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
import os
import logging
from django_celery_beat.models import IntervalSchedule, PeriodicTask


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
    scraper.novel_url = scrapeLink
    scraper.read_novel_info()
    
    return scraper

def add_chapter(chapter, queriedNovel):
    Chapter = apps.get_model('novels', 'Chapter')
    _, chapter = Chapter.objects.get_or_create(index = chapter['chapter']['id'],
                novelParent = queriedNovel, defaults={
                'text':chapter['body'],'title':chapter['chapter']['title'],
                'scrapeLink':chapter['chapter']['url']
            })

@shared_task
def initial_scrape(scrapeLink):
    Novel = apps.get_model("novels", "Novel")
    queriedNovel = Novel.objects.get(scrapeLink = scrapeLink)
    try:
        scraper = getNovelInfo(scrapeLink)
        queriedNovel.novelRef = scraper.novel_id

        results = scraper.executor.map(scraper.download_chapter_body,scraper.chapters)
        for result in results:
            add_chapter(result, queriedNovel)
            
        queriedNovel.repeatScrape = True
        queriedNovel.save()

    except requests.exceptions.SSLError:
        logger.error(f"Novel {queriedNovel.name} failed due to : Proxy error. Will restart later")
    
    except requests.exceptions.ConnectionError :
        logger.error(f"Novel {queriedNovel.name} failed due to : Connection error. Will restart later")

    except Exception as e:
        raise e
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

@shared_task
def continous_scrape(scrapeLink):
    Novel = apps.get_model("novels", "Novel")
    Chapter = apps.get_model("novels", "Chapter")
    queriedNovel = Novel.objects.get(scrapeLink = scrapeLink)
    try:
        if not queriedNovel.repeatScrape:
            return
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
        toScrape = [x for x in scraper.chapters if int(x['id']) > index]
        results = scraper.executor.map(scraper.download_chapter_body,toScrape)
        for result in results:
            add_chapter(result,queriedNovel)
    except requests.exceptions.SSLError:
        logger.error(f"Novel {queriedNovel.name} failed due to : Proxy error. Will restart later")
    except requests.exceptions.ConnectionError :
        logger.error(f"Novel {queriedNovel.name} failed due to : Proxy error. Will restart later")
    except Exception as e:
        logger.error(f"Novel {queriedNovel.name} failed due to : {e}")
        stop_repeat_scrape(queriedNovel)
    if scraper:
        scraper.destroy()

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
def new_novel(x):
    Novel = apps.get_model('novels', 'Novel')
    Tag = apps.get_model('novels', 'Tag')
    Category = apps.get_model('novels', 'Category')
    Author = apps.get_model('novels', 'Author')

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
    
    novel, _ = Novel.objects.get_or_create(slug = slugify(x['Book Name']), author = author,
            defaults = {'slug': slugify(x['Book Name']), 'name' : x['Book Name'], 'image' : x['Book Image'], 'imageThumb' : x['thumbnail'],
            'linkNU' : x['Book URL'], 'description' : x['Description'], 'numOfChaps' : int(x['Book Chapters'].strip().split(" ")[0]),
            'numOfTranslatedChaps' : 0, 'novelStatus' : False , 'scrapeLink' : x['novelLink'], 'repeatScrape' : True,
            'sources':'WuxSite'})
    
    novel.category.set(categoriesToPut)
    novel.tag.set(tagsToPut)
    novel.save()

@shared_task
def add_novels():
    df = pd.read_csv('actual.csv').astype(str)
    df.applymap(lambda x: "" if len(x)>199 else x)
    for _ , x in df.iterrows():
        new_novel.delay(x.to_dict())
        
        


            

