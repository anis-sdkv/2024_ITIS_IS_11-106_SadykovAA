from WebCrawler import WebCrawler

if __name__ == "__main__":
    crawler = WebCrawler("https://ru.wikipedia.org/wiki", False, 200)
    crawler.crawl()