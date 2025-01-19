import re

from bs4 import BeautifulSoup
from faker import Faker
import httpx


class Content:
    """
        Common base class for all articles/pages
            return Content(topic, url, title, body)
    """

    def __init__(self, url, title, body, author, date):
        self.url = url
        self.title = title
        self.body = body
        self.author = author
        self.date = date

    def print(self):
        """"
        Flexible printing function controls outputs
        """
        print(f'URL: {self.url}\n')
        print(f'TITLE: {self.title}')
        print(f'AUTHOR: {self.author}\n')
        print(f'Date: {self.date}\n')
        print(f'BODY: {self.body.strip("\n")}\n')


class Website:
    def __init__(self, name, url, target_pattern, absolute_url, title_tag, body_tag, author_tag, date_tag):
        self.name = name
        self.url = url
        self.target_pattern = target_pattern
        self.absolute_url = absolute_url
        self.title_tag = title_tag
        self.body_tag = body_tag
        self.author_tag = author_tag
        self.date_tag = date_tag


class Request:
    def __init__(self, website):
        self.site = website
        self.visited = {}

    def headers(self):
        fake = Faker()

        headers = {
            "User-Agent": fake.user_agent(),
            "Accept": fake.mime_type(),
            "Accept-Language": fake.language_code(),
            "Accept-Encoding": fake.word(),
            "Connection": "keep-alive"
        }
        return headers

    def fetch_content(self, url):
        response = None
        """Fetches the content of the page and returns a BeautifulSoup object"""
        try:
            with httpx.Client() as client:
                response = client.get(url, headers=self.headers())
                response.raise_for_status()
        except httpx.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')

        if response and response.status_code == 200:
            return BeautifulSoup(response.text, 'html.parser')
        else:
            return None

    def crawl(self):
        """
        Get pages from website homepage
        """
        content = self.fetch_content(url=self.site.url)
        links = content.find_all("a", href=re.compile(self.site.target_pattern))
        for link in links:
            url = link.attrs["href"]

            url = url if self.site.absolute_url else f"{self.site.url}{url}"
            if url not in self.visited:
                self.visited[url] = self.scrape(url=url)
            print(f"Scraped {url}")
            self.visited[url].print()

    def scrape(self, url):
        """Scrapes the contents of the page"""
        content = self.fetch_content(url=url)
        if content:
            title = self.safe_get(content, self.site.title_tag)
            body = self.safe_get(content, self.site.body_tag)
            author = self.safe_get(content, self.site.author_tag)
            date = content.select_one(self.site.date_tag)

            if date:
                date = date.text
            else:
                date = "Date not found"
            return Content(url, title, body, author, date)
        else:
            return Content(url, "Title not found", "Page not found", "", "")

    def safe_get(self, page_object, selector):
        """Extracts content from a BeautifulSoup object"""
        selected_elements = page_object.select(selector)
        if selected_elements is not None and len(selected_elements) > 0:
            return '\n'.join([element.get_text(strip=True, separator=' ') for element in selected_elements])
        return ''


site_data = [{
    "name": "Oxford",
    "url": "https://www.ox.ac.uk/news-and-events",
    "target_pattern": r"https://www.ox.ac.uk/news/",
    "absolute_url": True,
    "title_tag": "h1",
    "body_tag": "div span.field-item-single",
    "author_tag": "author",
    "date_tag": "time"
},
    {
        "name": "CNN",
        "url": "https://edition.cnn.com",
        "target_pattern": r"^\/\d{4}",
        "absolute_url": False,
        "title_tag": "h1",
        "body_tag": "div.article__content",
        "author_tag": "byline__name",
        "date_tag": "div.timestamp"
    }, {
        "name": "BBC",
        "url": "https://www.bbc.com",
        "target_pattern": r"^/news/articles",
        "absolute_url": False,
        "title_tag": "h1",
        "body_tag": "div.sc-18fde0d6-0.dlWCEZ p",
        "author_tag": "span.sc-2b5e3b35-7.bZCrck",
        "date_tag": "time.sc-2b5e3b35-2"
    }]

for site in site_data:
    request = Request(Website(**site))
    request.crawl()

# class Article:
#     """Contains information for scraping an article page"""
#     def __init__(self, name, url, title_tag,body_tag, date_tag):
#         Website.__init__(self, name, url, title_tag, body_tag)
#         self.date_tag = date_tag
