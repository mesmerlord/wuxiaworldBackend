from celery import shared_task
from django.apps import apps
import requests 
import pandas as pd
from django.utils.text import slugify
import json
from os import listdir
from urllib.parse import urlparse
from os.path import join
import os
import logging
from wuxiaworld.novels.utils import delete_dupes, delete_unordered_chapters
from django.conf import settings


logger = logging.getLogger("sentry_sdk")

chapters_folder = "chapters"


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
        
        
        
        novel, _ = Novel.objects.get_or_create(slug = slugify(x['Book Name']), author = author,
                defaults = {'slug': slugify(x['Book Name']), 'name' : x['Book Name'], 'image' : x['Book Image'], 'imageThumb' : x['thumbnail'],
                'linkNU' : x['Book URL'], 'description' : x['Description'], 'numOfChaps' : int(x['Book Chapters'].strip().split(" ")[0]),
                'novelStatus' : False , 'repeatScrape' : True,
                })
        
        novel.category.set(categoriesToPut)
        novel.tag.set(tagsToPut)
        novel.save()
    except Exception as e:
        print(e)
@shared_task
def add_novels():
    df = pd.read_csv(f'both.csv', keep_default_na=False).astype(str)
    df.applymap(lambda x: "" if len(x)>199 else x)
    for _ , x in df.iterrows():
        new_novel.delay(x.to_dict())

@shared_task
def add_sources():
    Source = apps.get_model("scraper", "Source")
    Novel = apps.get_model("novels", "Novel")

    with open("data.json", 'r', encoding= 'utf-8') as json_file:
        data = json.load(json_file)

    for novel in data:
        # print(novel)
        try:
            queriedNovel = Novel.objects.get(name = novel)
        except:
            continue
        for num, source in enumerate(data[novel][::-1]):
            try:
                base_url = urlparse(source[1]).netloc
            except:
                base_url = ""
            if num == len(data[novel]):
                disabled = True
            else:
                disabled = False
            new_source, _ = Source.objects.get_or_create(url = source[1],
            source_novel = queriedNovel ,defaults = {'disabled' : disabled,
            'base_url':base_url})
    
        
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

def check_if_image_in_media(image_file):
    path_to_media = join(settings.MEDIA_ROOT, 'novel_images')
    if not os.path.exists(path_to_media):
        os.makedirs(path_to_media)
    list_of_images = os.listdir(path_to_media)
    if image_file in list_of_images:
        return True
    else:
        return False

@shared_task()
def download_images():
    NovelViews = apps.get_model('novels', 'NovelViews')
    novels = NovelViews.objects.all()
    