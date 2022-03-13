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
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from urllib.request import urlretrieve
from PIL import Image
from django.core.files import File 
from django.core.cache import cache

# logger = logging.getLogger("sentry_sdk")

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

@shared_task
def add_views():
    NovelViews = apps.get_model('novels', 'NovelViews')
    views = cache.get('views')
    if not views:
        return
    for name, viewNum in views.items():
        novel = NovelViews.objects.get(viewsNovelName = name)
        novel.updateViews(increment_num = viewNum)
    cache.delete_pattern("views")
  
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

def get_image_from_url(url, novel):
    media_url = settings.MEDIA_ROOT
    original = f"{media_url}/original/"
    full_folder = f"{media_url}/full/"
    thumbnail_folder = f"{media_url}/thumbnail/"
    if not (os.path.exists(original) and os.path.exists(full_folder) and \
        os.path.exists(thumbnail_folder)):
        os.makedirs(original)
        os.makedirs(full_folder)
        os.makedirs(thumbnail_folder)

    result = urlretrieve(url, f"{original}/{novel.slug}.jpg")

    img = Image.open(f"{original}/{novel.slug}.jpg")    
    im = img.resize((300, 375), Image.ANTIALIAS)
    im_small = img.resize((150, 210), Image.ANTIALIAS)
    im.save(f"{novel.slug}-full.jpg")
    im_small.save(f"{novel.slug}-thumb.jpg")

    novel.new_image.save(f"{novel.slug}-full.jpg", im)
    novel.new_image_thumb.save(f"{novel.slug}-thumb.jpg", im_small)
    novel.original_image.save(f"{novel.slug}.jpg", img)
    novel.save()

@shared_task()
def download_images():
    Novel = apps.get_model('novels', "Novel")
    novels = Novel.objects.all()
    for novel in novels[:10]:
        if novel.image:
            try:
                get_image_from_url(novel.image, novel)
            except Exception as e:
                print(e)
                continue
