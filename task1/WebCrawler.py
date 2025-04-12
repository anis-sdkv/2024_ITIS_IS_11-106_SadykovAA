import os
import time
import urllib.parse
import requests
from collections import deque
from bs4 import BeautifulSoup

class WebCrawler:
    def __init__(self, start_url, domain_restriction=True, max_pages=100, delay=1):
        self.start_url = start_url
        self.domain_restriction = domain_restriction
        self.max_pages = max_pages
        self.delay = delay

        parsed_url = urllib.parse.urlparse(start_url)
        self.base_domain = parsed_url.netloc

        self.urls_to_visit = deque([start_url])
        self.visited_urls = set()

    @staticmethod
    def get_domain(url):
        parsed_url = urllib.parse.urlparse(url)
        return parsed_url.netloc

    def is_valid_url(self, url):
        if self.domain_restriction and self.get_domain(url) != self.base_domain:
            return False
        return True

    @staticmethod
    def is_russian_page(soup):
        html_tag = soup.find('html')
        if html_tag and 'lang' in html_tag.attrs:
            lang = html_tag['lang'].lower()
            return lang.startswith('ru')
        return False

    @staticmethod
    def is_russian_text(text, threshold=0.3):
        cyrillic_count = sum(1 for char in text if '\u0400' <= char <= '\u04FF')
        total_letters = sum(1 for char in text if char.isalpha())

        if total_letters == 0:
            return False

        return (cyrillic_count / total_letters) >= threshold

    @staticmethod
    def is_russian_by_headers(response):
        content_language = response.headers.get('Content-Language', '').lower()
        return content_language.startswith('ru')

    def extract_links(self, soup, base_url):
        links = set()
        all_links = soup.find_all('a', href=True)

        for link in all_links:
            href = link['href']
            if href.startswith("#"):
                continue
            if href.startswith('/'):
                href = urllib.parse.urljoin(base_url, href)
            if self.is_valid_url(href):
                links.add(href)
        return links

    @staticmethod
    def save_text_to_file(filename, text):
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(text)
            print(f'Текст успешно сохранен в файл: {filename}')
        except Exception as e:
            print(f'Ошибка при сохранении файла: {e}')

    @staticmethod
    def extract_text_from_page(soup):
        return soup.get_text(separator=' ', strip=True)

    def crawl(self):
        print(f"Starting to crawl from {self.start_url}")
        base_dir = f"out/{self.base_domain}"
        os.makedirs(base_dir, exist_ok=True)

        page_num = 0

        with open(f'{base_dir}/index.txt', 'w', encoding='utf-8') as crawled_urls:
            while self.urls_to_visit and page_num <= self.max_pages:
                current_url = self.urls_to_visit.popleft()

                if current_url in self.visited_urls:
                    continue

                decoded_url = urllib.parse.unquote(current_url)
                print(f"Crawling: {decoded_url}")

                try:
                    response = requests.get(current_url, timeout=10)
                    content_type = response.headers.get('Content-Type', '').lower()
                    self.visited_urls.add(current_url)

                    if response.status_code == 200 and 'html' in content_type:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        content = self.extract_text_from_page(soup)

                        if not (self.is_russian_page(soup) or
                                self.is_russian_by_headers(response) or
                                self.is_russian_text(content)):
                            print(f"Пропускаем {current_url} - не русскоязычная страница")
                            continue


                        if len(content.split(' ')) < 1000:
                            continue

                        self.save_text_to_file(f'{base_dir}/page_{page_num}.txt', content)
                        crawled_urls.write(f"page_{page_num}: {decoded_url}\n")

                        if len(self.urls_to_visit) < self.max_pages * 2:
                            for link in self.extract_links(soup, current_url):
                                if link not in self.visited_urls:
                                    self.urls_to_visit.append(link)
                    page_num += 1

                    time.sleep(self.delay)

                except Exception as e:
                    print(f"Error crawling {current_url}: {e}")

        print(f"Crawling complete. Visited {len(self.visited_urls)} pages.")
