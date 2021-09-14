from celery import shared_task
# from .models import Category, Author, Novel, Chapter,NovelViews
from django.apps import apps
from datetime import datetime
import requests 
from bs4 import BeautifulSoup
import pandas as pd
from django.utils.text import slugify
import json
from os import listdir
from celery.task import periodic_task 
from celery.schedules import crontab
import cloudscraper
import random

headers = {
    'authority': 'wuxiaworld.site',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    'sec-ch-ua-mobile': '?0',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'none',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'accept-language': 'en-US,en;q=0.9'}

def get_response(url):
    proxyList = pd.read_csv("prox.csv")['prox'].values.tolist()

    for x in range(20):

        splitprox = random.choice(proxyList).split(":")
        proxyy = f'http://{splitprox[2]}:{splitprox[3]}@{splitprox[0]}:{splitprox[1]}'
        scraper = cloudscraper.create_scraper()
        try:
            response = scraper.get(url, headers = headers, proxies = {'http':proxyy, 'https':proxyy})
 
            if response:
                break
        except:
            continue
    return response
@shared_task
def scrape_chapter(novelLink,link,chapTitle, chapIndex):
    Novel = apps.get_model('novels', 'Novel')
    Chapter = apps.get_model('novels', 'Chapter')
    NovelViews = apps.get_model('novels', 'NovelViews')

    novel = Novel.objects.get(scrapeLink = novelLink)

    response = get_response(link)
    soup = BeautifulSoup(response.content,'lxml')
    chapLines = soup.find('div','text-left').find_all('p')
    allChaps = []
    for chapLine in chapLines: 
        allChaps.append(chapLine.get_text())
    allChapJoin = "\n".join(allChaps)
    chapter = Chapter.objects.create(index = chapIndex+1,text= allChapJoin,title = chapTitle,
                    novelParent = novel,scrapeLink = link)
def getNovelPage(link):

    response = get_response(link)
    soup = BeautifulSoup(response.content,'lxml')
    novelId = soup.find("input", class_ = "rating-post-id").attrs['value']
    
    return {'soup':soup,'novelId':novelId}

def getChapsOld(link, first_run = False):
    Novel = apps.get_model('novels', 'Novel')
    Chapter = apps.get_model('novels', 'Chapter')
    NovelViews = apps.get_model('novels', 'NovelViews')
    scraper = cloudscraper.create_scraper()
    
    if first_run:
        scrapedNovel = getNovelPage(link)
        novel_id = scrapedNovel['novelId']
    else:
        currentNovel = Novel.objects.get(scrapeLink = link)
        novel_id_temp = currentNovel.novelRef
        if not novel_id_temp :
            scrapedNovel = getNovelPage(link)
            novel_id = scrapedNovel['novelId']
            currentNovel.novelRef = novel_id
            currentNovel.save()

        else:
            novel_id = novel_id_temp

    try:
        
        data = {
        'action': 'manga_get_chapters',
        'manga': f'{novel_id}'
        }
        adminLink = "https://wuxiaworld.site/wp-admin/admin-ajax.php"
        apiResponse = scraper.post(adminLink,headers = headers,data = data)
        apiSoup = BeautifulSoup(apiResponse.content,'lxml')
        chapters = apiSoup.find_all('li',class_ = "wp-manga-chapter")
    except:
        chapters = None
        print("error happened")
        
    
    return {'chapters':chapters, 'id': novel_id}
    

@shared_task
def initial_scrape(link):
    allScrape = getChapsOld(link,first_run = True)
    chapters = allScrape['chapters']
    Novel = apps.get_model('novels', 'Novel')
    currentNovel = Novel.objects.get(scrapeLink = link)
    currentNovel.novelRef = allScrape['id']
    currentNovel.save()
    for y,x in enumerate(chapters[::-1]):

        chap = x.find("a")
        chapTitle = chap.get_text().strip()
        scrape_chapter.delay(link,chap.attrs['href'],chapTitle,y)
        
@shared_task
def continous_scrape(scrapeLink):
    Novel = apps.get_model('novels', 'Novel')
    Chapter = apps.get_model('novels', 'Chapter')

    novelToSearch = Novel.objects.get(scrapeLink = scrapeLink)
    try:
        chapters = getChapsOld(scrapeLink)['chapters']
    except Exception as e:
        raise Exception(f"Novel {novelToSearch.name} failed to get chapters.")
        return "Finished with error - Failed to get chapter"
    allChapters =  Chapter.objects.filter(novelParent = novelToSearch).order_by("index")
    index = allChapters.count()
    lastChapLink = allChapters.last().scrapeLink
    chapsToScrape = []
    for x in chapters:
        chap_obj = x.find("a")
        if lastChapLink == chap_obj.attrs['href']:
            break
        chapsToScrape.append(x)
   
    for chap in chapsToScrape[::-1]:
        index += 1
        chap_obj = chap.find("a")
        chapTitle = chap_obj.get_text().strip()
        scrape_chapter.delay(scrapeLink,chap_obj.attrs['href'],chapTitle,index)
        

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
def new_novel(aDict,categoriesToPut,tagsToPut):
    Novel = apps.get_model('novels', 'Novel')
    try:
        novel, _ = Novel.objects.get_or_create(slug = aDict['slug'],
                                defaults = aDict)
        novel.category.set(categoriesToPut)
        novel.tag.set(tagsToPut)
        novel.save()
    except Exception:
        pass

@shared_task
def add_novels():
    df = pd.read_csv('actual.csv')
    
    for _ , x in df.iterrows():
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
            print(f"Book {x['Book Name']} , author {x['Book Author']} already exists")
        novelCheck  = Novel.objects.filter(slug = slugify(x['Book Name']))
       
        if not novelCheck :
            newDict = {'slug': slugify(x['Book Name']), 'name' : x['Book Name'], 'image' : x['Book Image'], 'imageThumb' : x['thumbnail'],
                        'linkNU' : x['Book URL'], 'author' : author, 'description' : x['Description'], 'numOfChaps' : int(x['Book Chapters'].strip().split(" ")[0]),
                        'numOfTranslatedChaps' : 0, 'novelStatus' : False , 'scrapeLink' : x['novelLink'], 'repeatScrape' : True}
            new_novel.delay(newDict, categoriesToPut, tagsToPut)
        
            

