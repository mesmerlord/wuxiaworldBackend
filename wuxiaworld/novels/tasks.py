from celery import shared_task
from .models import Category, Author, Novel, Chapter
import requests 
from bs4 import BeautifulSoup
import pandas as pd
from django.utils.text import slugify
import json
from os import listdir

@shared_task
def addCat():
    dfCat = pd.read_csv(r'newfile3.csv', sep=',')
    categories = []
    catList = dfCat['Book Genre'].values.tolist()
    doneList = []
    for i in catList:
        catNames = i.split(':')
        for x in catNames:
            if x not in doneList:
                tempVal = Category(
                    name=x,
                    slug=slugify(x))
                categories.append(tempVal)
                doneList.append(x)
    Category.objects.bulk_create(categories)

@shared_task
def addNovel():
    dfNovel = pd.read_csv(r'newfile3.csv', sep=',')
    # novels = []
    novelList = dfNovel.values.tolist()
    doneList = []
    with open("categories.json",'r') as newfile:
        reader = newfile.read()
        jsonData = json.loads(reader)
        for i in novelList:
            catList = []
            if i[1] not in doneList:
                if i[11]=="Ongoing":
                    status = True
                else:
                    status = False 
                try:
                    author, _= Author.objects.get_or_create(slug = slugify(i[4]), name = i[4])
                except:
                    print(i[4],slugify(i[4]) )
                    author = None
                try:
                    tempVal = Novel(
                        name=i[1],
                        image=i[3],
                        linkNU=i[0],
                        author= author,
                        description=i[8],
                        slug = slugify(i[1]),
                        numOfChaps = int(i[10].strip().split(" ")[0]),
                        novelStatus=status,
                        )
                
                    tempVal.save()
                    for y in i[2].split(":"):
                        for catName in jsonData:
                            if catName['name'] == y:
                                catId = catName['id']
                        catObj = Category.objects.get(id = catId)
                        print(catObj)
                        print(catObj.pk)

                        try:
                            tempVal.category.add(catObj)
                            print("worked")
                        except Exception as e:
                            print(e)
                            try:
                                tempVal.category.add(catObj.pk)
                            except  Exception as e:
                                print(e)
                                tempVal.category.add(catObj.slug)
                except :
                    continue
                # novels.append(tempVal)
                doneList.append(i[1])

@shared_task
def addChaps():
    for novelFile in listdir("."):
        if ".csv" in novelFile and "file" not in novelFile:

            dfChapter = pd.read_csv(f'media/{novelFile}', sep=',',chunksize=10000)
            # novels = []
            for chunk in dfChapter:
                chaplist = chunk.values.tolist()
                doneList = []
                for x in chaplist:
                    if x[2] not in doneList:
                        try:
                            chapter = Chapter(
                                text = x[1],
                                title = x[3],
                                novelParent = Novel.objects.get(slug = x[6])

                            )
                            chapter.save()
                            doneList.append(x[2]) 
                        except:
                            continue



@shared_task
def add(num,num2):
    return str(num+num2)