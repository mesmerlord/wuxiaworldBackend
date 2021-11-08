# -*- coding: utf-8 -*-
import json
import logging
import re
from .crawler import Crawler

logger = logging.getLogger(__name__)
search_url = 'https://readnovelfull.com/search?keyword=%s'
full_chapter_url = 'https://readnovelfull.com/ajax/chapter-archive?novelId=%s'


class ReadNovelFullCrawler(Crawler):
    base_url = 'https://readnovelfull.com/'

    def search_novel(self, query):
        query = query.lower().replace(' ', '+')
        soup = self.get_soup(search_url % query)

        results = []
        for result in soup.select('div.col-novel-main div.list.list-novel div.row')[:5]:
            url = self.absolute_url(
                result.select_one('h3.novel-title a')['href'])
            title = result.select_one('h3.novel-title a')['title']
            last_chapter = result.select_one('span.chr-text').text.strip()
            results.append({
                'url': url,
                'title': title,
                'info': 'last chapter : %s' % last_chapter,
            })
        # end for
        return results
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        soup = self.get_soup(self.novel_url + '?waring=1')

        self.novel_title = soup.select_one('h3.title').text.strip()

        self.novel_cover = self.absolute_url(
            soup.select_one('div.book img')['src'])

        author = []
        for a in soup.select('ul.info.info-meta li')[1].select('a'):
            author.append(a.text.strip())
        # end for

        self.novel_author = ", ".join(author)


        novel_id = soup.select_one('div#rating')['data-novel-id']

        chapter_url = full_chapter_url % novel_id

        chapter_soup = self.get_soup(chapter_url)
        chapters = chapter_soup.select('li a')
        for a in chapters:
            for span in a.findAll('span'):
                span.extract()
            # end for
        # end for

        for x in chapters:
            chap_id = len(self.chapters) + 1
            if len(self.chapters) % 100 == 0:
                vol_id = chap_id//100 + 1
                vol_title = 'Volume ' + str(vol_id)
                self.volumes.append({
                    'id': vol_id,
                    'title': vol_title,
                })
            # end if
            url = x["href"]
            if "readnovel" not in url:
                url = f"https://readnovelfull.com{url}"
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'url': url,
                'title': x['title'] or ('Chapter %d' % chap_id),
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        soup = self.get_soup(chapter['url'])
        content = soup.select_one('#chr-content')
        return {'chapter':chapter,'body':self.extract_contents(content)}
    # end def
# end class
