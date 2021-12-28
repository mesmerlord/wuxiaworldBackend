from wuxiaworld.novels.models import Chapter, Novel
from wuxiaworld.scraper.models import Source
from urllib.parse import urlparse

chapters = Chapter.objects.all()
empty_chapters = chapters.filter(text = "")
count_empty = empty_chapters.count()

sources = {}
for empty_chapter in empty_chapters:
    chapLink = empty_chapter.scrapeLink
    novelPar = empty_chapter.novelParent
    parsed_url = urlparse(chapLink)
    base_url = '%s://%s/' % (parsed_url.scheme, parsed_url.hostname)
    empty_source = Source.objects.filter(url__icontains = base_url).filter(source_novel = novelPar).first()
    if not empty_source:
        continue
    empty_source.delete()
    # if empty_source.base_url in sources:
    #     sources[empty_source.base_url] += 1
    # else:
    #     sources[empty_source.base_url] = 0

