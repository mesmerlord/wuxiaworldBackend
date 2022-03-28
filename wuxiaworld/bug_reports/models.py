from django.db import models
from wuxiaworld.novels.models import Novel
from django.utils.timezone import now
from wuxiaworld.scraper.signals import remove_chapters

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add= True)
    updated_at = models.DateTimeField(auto_now= True)
    class Meta:
        abstract = True

class BugReport(BaseModel):
    ISSUE_CHOICES = (
        ("CO", "Chapter Overflow"),
        ("GI", "General Issue"),
        ("CE", "Chapter Empty"),
        ("COO", "Chapter Out Of Order"),
        ("NHNF", "Novel Hot Not Found"),

    )
    title = models.CharField(max_length = 100)
    description = models.TextField()
    checked = models.BooleanField(default = False)
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, null = True, blank = True)
    issue_type = models.CharField(max_length = 5, choices = ISSUE_CHOICES)

    class Meta:
        unique_together = ('novel', "description")
        ordering = ["-novel__ranking"]