# -*- coding: utf-8 -*-
import logging
from .crawler import Crawler

search_url = 'https://vipnovel.com/?s=%s&post_type=wp-manga&author=&artist=&release='


class VipNovel(Crawler):
    base_url = 'https://vipnovel.com/'

    def search_novel(self, query):
        query = query.lower().replace(' ', '+')
        soup = self.get_soup(search_url % query)

        results = []
        for tab in soup.select('.c-tabs-item__content')[:20]:
            a = tab.select_one('.post-title h4 a')
            latest = tab.select_one('.latest-chap .chapter a').text
            votes = tab.select_one('.rating .total_votes').text
            results.append({
                'title': a.text.strip(),
                'url': self.absolute_url(a['href']),
                'info': '%s | Rating: %s' % (latest, votes),
            })
        # end for

        return results
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('.post-title h1')
        for span in possible_title.select('span'):
            span.extract()
        # end for
        self.novel_title = possible_title.text.strip()

        self.novel_cover = self.absolute_url(
            soup.select_one('.summary_image a img')['src'])
        self.novel_author = ' '.join([
            a.text.strip()
            for a in soup.select('.author-content a[href*="manga-author"]')
        ])

        self.novel_id = soup.select_one("#manga-chapters-holder")["data-id"]

        response = self.submit_form(self.novel_url.strip('/') + '/ajax/chapters')
        soup = self.make_soup(response)
        chapters = soup.select(".wp-manga-chapter a")
        if not chapters:
            newChapLink = f"{self.novel_url}ajax/chapters/"
            soup = self.make_soup(self.submit_form(
            newChapLink,
            
            headers = {
                'origin': 'https://vipnovel.com',
                'user-agent':' Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'
            }
            ))
            chapters = soup.select('li.wp-manga-chapter a')
        for a in reversed(chapters):
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if chap_id % 100 == 1:
                self.volumes.append({"id": vol_id})
            # end if
            url = a["href"]
            
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "title": a.text.strip(),
                    "url": url,
                }
            )
        # end for
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        soup = self.get_soup(chapter['url'])

        contents = soup.select_one('div.text-left')
        for bad in contents.select('h3, .code-block, script, .adsbygoogle'):
            bad.extract()

        return {'chapter':chapter,'body':self.extract_contents(contents)}
    # end def
# end class
