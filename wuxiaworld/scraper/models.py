from django.db import models
from wuxiaworld.novels.models import Novel
from django.utils.timezone import now

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add= True)
    updated_at = models.DateTimeField(auto_now= True)
    class Meta:
        abstract = True

class Source(BaseModel):
    url = models.CharField(max_length=200, unique=True)
    source_novel = models.ForeignKey(Novel, on_delete= models.CASCADE)
    disabled = models.BooleanField(default = False)
    priority = models.IntegerField(default = 0)
    base_url = models.CharField(max_length=200)

    def save(self,*args, **kwargs):
        if not self.priority:
            self.priority = Source.objects.filter(source_novel = self.source_novel).count() + 1
        super(Source, self).save(*args, **kwargs)
