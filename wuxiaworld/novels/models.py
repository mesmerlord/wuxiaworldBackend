from django.db import models
from rest_framework import serializers
from django.utils.text import slugify

# Create your models here.

class Author(models.Model):
    name = models.CharField(max_length = 50)
    slug = models.SlugField(max_length = 50, primary_key=True)
    def __str__(self):
        return self.name

class Category(models.Model):
    #Also used for language instead of creating a new model
    name = models.CharField(max_length = 50)
    slug = models.CharField(max_length = 50, blank = True)
    def __str__(self):
        return self.name
    def save(self,*args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.index:
            self.index = Category.objects.all().count()+1
        super(Category, self).save(*args, **kwargs)

class Novel(models.Model):
    name = models.CharField(max_length = 100)
    views = models.IntegerField(default = 0)
    image = models.URLField(blank = True)
    linkNU = models.URLField(blank = True)
    author = models.ForeignKey(Author, on_delete = models.CASCADE, null = True)
    category = models.ManyToManyField(Category)
    description = models.TextField(blank = True)
    slug = models.SlugField(primary_key = True, default = None, max_length=100)
    numOfChaps = models.IntegerField(default = 0)
    novelStatus = models.BooleanField(default = True) #True will be for Ongoing, False for Completed
    def __str__(self):
        return self.name



class Chapter(models.Model):
    index = models.IntegerField(default = None, blank = True)
    text = models.TextField(max_length=None)
    title = models.TextField(max_length = 100)
    novelParent = models.ForeignKey(Novel, on_delete = models.CASCADE, verbose_name = "chapter")
    nextChap = models.BooleanField(default = False)
    novSlugChapSlug = models.CharField( max_length = 100, blank = True, default = None)
    def save(self, *args, **kwargs):
        if not self.index:
            self.index = Chapter.objects.filter(novelParent = self.novelParent).count()+1
            try:
                lastChap = Chapter.objects.get(novelParent = self.novelParent, index = self.index-1)
                if lastChap:
                    lastChap.nextChap = True
                    lastChap.save()
            except:
                pass
        if not self.novSlugChapSlug:
            self.novSlugChapSlug = f"{self.novelParent.slug}-{self.index}"
        super(Chapter, self).save(*args, **kwargs)
    def __str__(self):
        return f"Chapter {self.index} - {self.novelParent}"





    