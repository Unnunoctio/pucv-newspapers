import asyncio
import math
import re
import time
from datetime import datetime
from typing import Any, List, Optional

from bs4 import BeautifulSoup

from core.models import Article, DateRange
from crawler._base import BaseCrawler
from utils.date_utils import DateUtils
from utils.fetcher_manager import FetcherManager as FM
from utils.logger import Logger


class StaticWebsiteCrawler(BaseCrawler):
    """Crawler for static websites"""

    def __init__(self, config: dict, date_range: DateRange):
        super().__init__(config, date_range)
        self.PAGES_CONFIG = config.get("pages_config")
        self.ARTICLES_LIST_CONFIG = config.get("articles_list_config")
        self.ARTICLE_CONFIG = config.get("article_config")

    # TODO: GENERATE PAGES
    def generate_pages(self, base_url: str) -> List[str]:
        """Generate the list of pages to crawl"""
        total_pages = self._get_total_pages(base_url)
        start_page = self._get_start_page(base_url, self.date_range.start_date, 1, total_pages)
        end_page = self._get_end_page(base_url, self.date_range.end_date, 1, start_page)

        Logger.info(prefix="INFO", message=f"Getting pages between: {end_page} and {start_page}")

        pages = []
        for i in range(end_page, start_page + 1):
            page_url = re.sub(r"\(\\s\+\)", base_url, self.PAGES_CONFIG.get("url_pattern"))
            page_url = re.sub(r"\(\\d\+\)", str(i), page_url)
            pages.append(page_url)

        return pages[::-1]

    def _get_total_pages(self, base_url: str) -> int:
        """Get the total number of pages"""
        url = re.sub(r"\(\\s\+\)", base_url, self.PAGES_CONFIG.get("url_pattern"))
        url = re.sub(r"\(\\d\+\)", str(1), url)

        html, status = FM.fetch_html(url=url, retry_delay=self.REQUESTS_CONFIG.get("retry_delay"))
        if status is None or status == 404:
            return 0

        # Format html
        soup = BeautifulSoup(html, "html.parser")
        pagination_config = self.PAGES_CONFIG.get("pagination")

        # Get items from pagination
        page_items = soup.select(pagination_config.get("selector"))
        last_item_url = page_items[pagination_config.get("pos_pagination_item")].get("href")

        # Get last page from pagination
        if pagination_config.get("split_href") is not None:
            return int(last_item_url.split(pagination_config.get("split_href"))[pagination_config.get("pos_href")])

        return int(last_item_url.split("/")[pagination_config.get("pos_href")])

    def _get_start_page(self, base_url: str, start_date: datetime, start_page: int, end_page: int) -> int:
        """Get the start page to crawl"""
        if start_page >= end_page - 1:
            return end_page

        mid_page = math.floor((start_page + end_page) / 2)

        url = re.sub(r"\(\\s\+\)", base_url, self.PAGES_CONFIG.get("url_pattern"))
        url = re.sub(r"\(\\d\+\)", str(mid_page), url)

        html, status = FM.fetch_html(url=url, retry_delay=self.REQUESTS_CONFIG.get("retry_delay"))
        if status is None or status == 404:
            return self._get_start_page(base_url, start_page, start_page + 1, end_page)

        # Format html
        soup = BeautifulSoup(html, "html.parser")
        datetime_config = self.ARTICLES_LIST_CONFIG.get("datetime")

        # Get items
        articles_date_items = soup.select(datetime_config.get("selector"))
        last_article_date_item = articles_date_items[-1]

        if datetime_config.get("attribute") is not None:
            last_article_date_str = last_article_date_item.get(datetime_config.get("attribute"))
        else:
            last_article_date_str = last_article_date_item.get_text(strip=True)

        last_article_date = datetime.strptime(last_article_date_str, datetime_config.get("format"))

        # Binary search logic
        diff = DateUtils.diff_days(start_date, last_article_date)
        if diff == 1:
            return mid_page
        elif diff > 1:
            return self._get_start_page(base_url, start_date, start_page, mid_page)
        else:
            return self._get_start_page(base_url, start_date, mid_page, end_page)

    def _get_end_page(self, base_url: str, end_date: datetime, start_page: int, end_page: int) -> int:
        """Get the end page to crawl"""
        if start_page >= end_page - 1:
            return start_page

        mid_page = math.floor((start_page + end_page) / 2)

        url = re.sub(r"\(\\s\+\)", base_url, self.PAGES_CONFIG.get("url_pattern"))
        url = re.sub(r"\(\\d\+\)", str(mid_page), url)

        html, status = FM.fetch_html(url=url, retry_delay=self.REQUESTS_CONFIG.get("retry_delay"))
        if status is None or status == 404:
            return self._get_end_page(base_url, start_page, start_page, end_page - 1)

        # Format html
        soup = BeautifulSoup(html, "html.parser")
        datetime_config = self.ARTICLES_LIST_CONFIG.get("datetime")

        # Get items
        articles_items = soup.select(self.ARTICLES_LIST_CONFIG.get("selector"))
        last_article_date_item = articles_items[-1].select_one(datetime_config.get("selector"))

        if datetime_config.get("attribute") is not None:
            last_article_date_str = last_article_date_item.get(datetime_config.get("attribute"))
        else:
            last_article_date_str = last_article_date_item.get_text(strip=True)

        last_article_date = datetime.strptime(last_article_date_str, datetime_config.get("format"))

        # Binary search logic
        diff = DateUtils.diff_days(end_date, last_article_date)
        if diff == -1:
            return mid_page
        elif diff < -1:
            return self._get_end_page(base_url, end_date, mid_page, end_page)
        else:
            return self._get_end_page(base_url, end_date, start_page, mid_page)

    # TODO: GET ARTICLES
    async def get_articles(self, pages: List[str]) -> List[Article]:
        """Get articles from the pages"""
        BLOCK_SIZE = int(self.REQUESTS_CONFIG.get("requests_per_minute") / 60)

        # Get all article urls
        all_articles_urls = []
        for i in range(0, len(pages), BLOCK_SIZE):
            start_time = time.time()
            article_urls = await self._get_articles_urls(pages[i:i+BLOCK_SIZE])
            all_articles_urls.extend(article_urls)
            await self._sleep_between_requests(start_time)
        
        Logger.info(prefix="SPIDER", message=f" Obteniendo {len(all_articles_urls)} artículos")

        # Get all articles from the urls
        all_articles = []
        for i in range(0, len(all_articles_urls), BLOCK_SIZE):
            start_time = time.time()
            articles = await self._get_articles(all_articles_urls[i:i+BLOCK_SIZE])
            all_articles.extend(filter(
                lambda a: (a is not None)
                and (a.date >= self.date_range.start_date and a.date <= self.date_range.end_date),
                articles
            ))
            await self._sleep_between_requests(start_time)
        
        return all_articles

    async def _get_articles_urls(self, pages: List[str]) -> List[str]:
        tasks = [self._get_article_urls(page) for page in pages]
        block_urls = await asyncio.gather(*tasks, return_exceptions=False)
        return [item for sublist in block_urls for item in sublist]

    async def _get_article_urls(self, page: str) -> List[str]:
        html, status = await FM.async_fetch_html(page, self.REQUESTS_CONFIG.get("retry_delay"), int(self.REQUESTS_CONFIG.get("requests_per_minute") / 60))
        if status is None or status == 404:
            return []

        # Format html
        soup = BeautifulSoup(html, "html.parser")
        selector = f"{self.ARTICLES_LIST_CONFIG.get('selector')} {self.ARTICLES_LIST_CONFIG.get('url').get('selector')}"

        # Get items
        article_links = soup.select(selector)
        article_urls = set()

        for article_link in article_links:
            article_url = article_link.get("href")
            if article_url is not None:
                if self.ARTICLES_LIST_CONFIG.get("url").get("prefix") is not None:
                    article_urls.add(f"{self.ARTICLES_LIST_CONFIG.get('url').get('prefix')}{article_url}")
                else:
                    article_urls.add(article_url)

        return list(article_urls)

    async def _get_articles(self, urls: List[str]) -> List[Article]:
        tasks = [self._get_article(url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=False)

    async def _get_article(self, url: str) -> Article | None:
        html, status = await FM.async_fetch_html(url, self.REQUESTS_CONFIG.get("retry_delay"), int(self.REQUESTS_CONFIG.get("requests_per_minute") / 60))
        if status is None or status == 404:
            return None

        try:
            article = self._parse_article(html, url)
            if article.date is None:
                Logger.error("DB", f"No se ha podido obtener los datos de la noticia: {url}")
                await asyncio.sleep(self.REQUESTS_CONFIG.get("retry_delay"))
                return await self._get_article(url)
            
            return article
        except Exception as e:
            Logger.error("ERROR", f"Error al procesar el artículo: {url} [Error: {e}]")
            return None

    # TODO: PARSE ARTICLE
    def _parse_article(self, html: Any, url: str) -> Article:
        # Change html to BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        # Create article
        article = Article(self.NAME, url)

        # TITLE
        title_elem = self._get_html_elem(soup, self.ARTICLE_CONFIG.get("title").get("selectors"))
        if title_elem is not None:
            article.title = title_elem.get_text(strip=True)

        # AUTHOR
        author_elem = self._get_html_elem(soup, self.ARTICLE_CONFIG.get("author").get("selectors"))
        if author_elem is not None:
            article.author = author_elem.get_text(strip=True)

        # DATE
        date_elem = self._get_html_elem(soup, self.ARTICLE_CONFIG.get("date").get("selectors"))
        if date_elem is not None:
            if self.ARTICLE_CONFIG.get("date").get("attribute") is not None:
                datetime_str = date_elem.get(self.ARTICLE_CONFIG.get("date").get("attribute"))
            else:
                datetime_str = date_elem.get_text(strip=True)

            article.date = datetime.strptime(datetime_str, self.ARTICLE_CONFIG.get("date").get("format"))

        # TAG
        tag_elem = self._get_html_elem(soup, self.ARTICLE_CONFIG.get("tag").get("selectors"))
        if tag_elem is not None:
            article.tag = tag_elem.get_text(strip=True)

        # DROPHEAD
        drophead_elem = self._get_html_elem(soup, self.ARTICLE_CONFIG.get("drophead").get("selectors"))
        if drophead_elem is not None:
            article.drophead = drophead_elem.get_text(strip=True)

        # BODY
        body_elem = self._get_html_elem(soup, self.ARTICLE_CONFIG.get("body").get("selectors"))
        if body_elem is not None:
            for remove_elem in self.ARTICLE_CONFIG.get("body").get("remove_elements"):
                for elem in body_elem.find_all(remove_elem):
                    elem.decompose()
            
            body_html = body_elem.decode_contents(formatter="html")
            self.body = self.HTML_PARSER.handle(body_html).strip()
            self.body_html = body_html

        return article

    def _get_html_elem(self, soup: BeautifulSoup, selectors: List[str]) -> Optional[Any]:
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem is not None:
                return elem

        return None

    # TODO: UTILS
    async def _sleep_between_requests(self, start_time: float) -> None:
        """Sleep between requests"""
        end_time = time.time()

        # Calculate the time to sleep
        time_to_sleep = 1 - (end_time - start_time)
        if time_to_sleep > 0:
            Logger.critical("TIMER", f"Sleeping for {time_to_sleep} seconds...")
            await asyncio.sleep(time_to_sleep)