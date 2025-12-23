import asyncio
import time
from datetime import datetime
from typing import Any, List, Optional, Tuple

from core.models import Article, DateRange
from crawlers._base import BaseCrawler
from services.fetcher_manager import FetcherManager
from utils.logger import Logger


class ApiCrawler(BaseCrawler):
    """Crawler for APIs"""

    def __init__(self, config: dict, date_range: DateRange):
        super().__init__(config, date_range)
        self.PAGINATION = config.get("pagination")
        self.ARTICLES_LIST_CONFIG = config.get("articles_list_config")
        self.ARTICLE_CONFIG = config.get("article_config")

        # Config a fetcher manager
        delay = self.REQUESTS_CONFIG.get("retry_delay")
        concurrent = int(self.REQUESTS_CONFIG.get("requests_per_minute") / 60)
        self.FETCHER = FetcherManager(retry_delay=delay, max_concurrent=concurrent)

    # TODO: GENERATE PAGES
    async def generate_pages(self, base_url) -> List[str]:
        pass

    # TODO: GET ARTICLES
    async def get_articles(self, pages: List[str]) -> List[Article]:
        pass

    # TODO: PARSE ARTICLE
    def _parse_article(self, article_json: Any) -> Article:
        # Get URL
        url = self._get_url(article_json)
        if url is None:
            Logger.error("DB", f"No se ha podido obtener el URL del artículo: {article_json}")
            return None

        # Create article
        article = Article(self.NAME, url)

        # TITLE
        title = self._get_title(article_json)
        if title is not None:
            article.title = title

        # AUTHOR
        author = self._get_author(article_json)
        if author is not None:
            article.author = author

        # DATE
        date = self._get_date(article_json)
        if date is not None:
            article.date = date

        # TAG
        tag = self._get_tag(article_json)
        if tag is not None:
            article.tag = tag

        # DROPHEAD
        drophead = self._get_drophead(article_json)
        if drophead is not None:
            article.drophead = drophead

        # BODY
        body, body_html = self._get_body(article_json)
        if body is not None:
            article.body = body
            article.body_html = body_html

        return article

    # TODO: ENCAPSULATION OF GET DATA FROM JSON
    def _get_url(self, data: Any) -> Optional[str]:
        url = self._get_attribute_safe(data, self.ARTICLE_CONFIG.get("url").get("paths"))
        return url

    def _get_title(self, data: Any) -> Optional[str]:
        title = self._get_attribute_safe(data, self.ARTICLE_CONFIG.get("title").get("paths"))
        return title

    def _get_author(self, data: Any) -> Optional[str]:
        author = self._get_attribute_safe(data, self.ARTICLE_CONFIG.get("author").get("paths"))
        return author

    def _get_date(self, data: Any) -> Optional[datetime]:
        date_str = self._get_attribute_safe(data, self.ARTICLE_CONFIG.get("date").get("paths"))
        if date_str is None:
            return None

        try:
            if self.ARTICLE_CONFIG.get("date").get("formats") is not None:
                for date_format in self.ARTICLE_CONFIG.get("date").get("formats"):
                    try:
                        if "T" in date_format:
                            new_date_format = date_format.split("T")[0]
                            new_date_str = date_str.split("T")[0]
                            article_date = datetime.strptime(new_date_str, new_date_format)
                        else:
                            article_date = datetime.strptime(date_str, date_format)

                        return article_date
                    except Exception:
                        pass
            else:
                date = datetime.strptime(date_str)
                return date
        except Exception:
            return None

        return None

    def _get_tag(self, data: Any) -> Optional[str]:
        tag = self._get_attribute_safe(data, self.ARTICLE_CONFIG.get("tag").get("paths"))
        return tag

    def _get_drophead(self, data: Any) -> Optional[str]:
        drophead = self._get_attribute_safe(data, self.ARTICLE_CONFIG.get("drophead").get("paths"))
        return drophead

    def _get_body(self, data: Any) -> Tuple[Optional[str], Optional[str]]:
        body_elem = self._get_attribute_safe(data, self.ARTICLE_CONFIG.get("body").get("paths"))
        if body_elem is None:
            return None, None

        if self.ARTICLE_CONFIG.get("body").get("is_html") is True:
            body_html = body_elem
            body = self.HTML_PARSER.handle(body_html).strip()
            return body, body_html

        return body_elem, None

    # TODO: UTILS
    def _get_nested_safe(self, data: Any, path: str) -> Optional[Any]:
        """Get a nested value from a dictionary, if the path doesn't exist, return None"""
        keys = path.split(".")

        try:
            result = data
            for key in keys:
                try:
                    key = int(key)
                except ValueError:
                    pass
                result = result[key]
            return result
        except (KeyError, IndexError, TypeError):
            return None

    def _get_attribute_safe(self, data: Any, paths: List[str]) -> Optional[Any]:
        """Get a nested value from a dictionary, if the path doesn't exist, return None"""
        for path in paths:
            data = self._get_nested_safe(data, path)
            if data is not None:
                return data

        return None

    async def _sleep_between_requests(self, start_time: float) -> None:
        """Sleep between requests"""
        end_time = time.time()

        # Calculate the time to sleep
        time_to_sleep = 1 - (end_time - start_time)
        if time_to_sleep > 0:
            Logger.critical("TIMER", f"Sleeping for {time_to_sleep} seconds...")
            await asyncio.sleep(time_to_sleep)
