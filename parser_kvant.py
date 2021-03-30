import os
import requests
import re
from tqdm import tqdm
from bs4 import BeautifulSoup


class ParserD:
    def __init__(self):
        self._site_url_1970_2003 = 'https://kvant.ras.ru/oblozhka_djvu.htm'
        self._site_url_2004_present = 'https://kvant.ras.ru/index.htm'

    @staticmethod
    def get_request(url):
        request = requests.get(url, stream=True)
        return request

    @staticmethod
    def get_link_1970_2003(url1970_2003):
        link_page = []
        download_links = []

        request = ParserD.get_request(url1970_2003).text
        soup = BeautifulSoup(request, 'lxml')
        all_tags_a = soup.findAll('a')
        for a in all_tags_a:
            if re.search('oblozhka', a['href'].partition('/')[0]):
                link_page.append('https://kvant.ras.ru/' + a['href'])

        for item in link_page:
            request = ParserD.get_request(item).text
            soup = BeautifulSoup(request, 'lxml')
            links = soup.findAll('a')

            for link in links:
                if link['href'].partition('/')[0] == 'djvu':
                    download_links.append('https://kvant.ras.ru/' + link['href'])
        return download_links

    @staticmethod
    def get_link_2004_present(url2004_present):
        download_links = []
        request = ParserD.get_request(url2004_present).text
        soup = BeautifulSoup(request, 'lxml')
        all_tags_a = soup.findAll('a')
        for a in all_tags_a:
            try:
                if a['href'].split('.')[-1] == 'pdf' or a['href'].split('.')[-1] == 'djvu' \
                        and not re.search('2003', a['href']):
                    download_links.append('https://kvant.ras.ru/' + a['href'])
            except KeyError:
                pass
        return download_links

    @staticmethod
    def create_folder():
        os.mkdir('Журнал Квант все выпуски')
        os.chdir('Журнал Квант все выпуски')

    """ Синхронное скачивание """
    def synchronous_download(self, links):
        for link in links:
            request = self.get_request(link)
            total_size = int(request.headers['content-length'])
            with open(f'{link.split("/")[-1]}', 'ab') as f:
                for data in tqdm(desc=link.split("/")[-1], iterable=request.iter_content(1024),
                                 total=int(total_size/1024), unit='KB', unit_scale=True, ):
                    f.write(data)

    def sync_main(self):
        links_1970_2003 = self.get_link_1970_2003(self._site_url_1970_2003)
        links_2004_present = self.get_link_2004_present(self._site_url_2004_present)
        links = links_1970_2003 + links_2004_present
        self.create_folder()
        self.synchronous_download(links)


if __name__ == '__main__':
    ParserD().sync_main()
