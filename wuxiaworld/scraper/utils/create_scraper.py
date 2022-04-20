from lncrawl.core.sources import load_sources, crawler_list
import urllib3
from urllib.parse import urlparse
from lncrawl.core.crawler import Crawler

urllib3.disable_warnings()

def init_crawler(novel_url) -> Crawler:
    if not novel_url:
        raise Exception('No novel url ')
    parsed_url = urlparse(novel_url)
    base_url = '%s://%s/' % (parsed_url.scheme, parsed_url.hostname)
    
    CrawlerType = crawler_list.get(base_url)
    if not CrawlerType:
        raise Exception('No crawler found for ' + base_url)

    crawler = CrawlerType()
    crawler.initialize()
    crawler.home_url = base_url
    crawler.novel_url = novel_url
    return crawler



def create_scraper(novel_url) -> Crawler:
    load_sources()
    novel_search = init_crawler(novel_url)
    novel_search.read_novel_info()
    return novel_search