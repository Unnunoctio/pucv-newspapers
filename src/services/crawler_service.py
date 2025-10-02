import asyncio
import math
import time
from typing import List

import yaml

from core.models import Article, DateRange
from crawlers._base import BaseCrawler
from services.excel_exporter import ExcelExporter
from utils.file_utils import FileUtils
from utils.logger import Logger


class CrawlerService:
    def __init__(self, start_date: str, end_date: str, crawler_to_run: dict):
        # Set date range
        try:
            self.date_range = DateRange(start_date, end_date)
        except Exception as e:
            Logger.error(prefix="ERROR", message=str(e))

        # Set crawlers
        self.crawlers: List[BaseCrawler] = []

        with open("src/config.yaml", "r") as f:
            data = yaml.safe_load(f)

        crawler_config_list = data.get("crawlers")

        def get_crawler_config(crawler_name: str):
            for crawler in crawler_config_list:
                if crawler.get("name") == crawler_name:
                    return crawler

        for key, value in crawler_to_run.items():
            if value is True:
                crawler_config = get_crawler_config(key)
                try:
                    if crawler_config.get("custom") is not None:
                        if crawler_config.get("custom") == "TVN":
                            from crawlers.customs.tvn import TVNCrawler

                            self.crawlers.append(TVNCrawler(crawler_config, self.date_range))
                        elif crawler_config.get("custom") == "COOPERATIVA":
                            from crawlers.customs.cooperativa import CooperativaCrawler

                            self.crawlers.append(CooperativaCrawler(crawler_config, self.date_range))
                        elif crawler_config.get("custom") == "EMOL":
                            from crawlers.customs.emol import EmolCrawler

                            self.crawlers.append(EmolCrawler(crawler_config, self.date_range))
                        else:
                            raise ValueError(f"Custom crawler [{crawler_config.get('custom')}] not supported")
                    else:
                        if crawler_config.get("type") == "STATIC_WEBSITE":
                            from crawlers.generics.static_website import StaticWebsiteCrawler

                            self.crawlers.append(StaticWebsiteCrawler(crawler_config, self.date_range))
                        elif crawler_config.get("type") == "API":
                            from crawlers.generics.api import ApiCrawler

                            self.crawlers.append(ApiCrawler(crawler_config, self.date_range))
                        else:
                            raise ValueError(f"Crawler type [{crawler_config.get('type')}] not supported")
                except Exception as e:
                    Logger.error(prefix="ERROR", message=str(e))

        # Set stats
        self.stats = []

    def run(self) -> None:
        for crawler in self.crawlers:
            start_time = time.time()
            articles = asyncio.run(crawler.crawl())
            end_time = time.time()

            Logger.info("TIMER", f"{crawler.NAME.value}: {self._print_time(end_time - start_time)}")

            self.stats.append({"site_name": crawler.NAME.value, "articles": len(articles), "time": end_time - start_time})
            self._save_articles(articles)

        self._print_stats()

    def _print_time(self, time: float) -> str:
        hours = math.floor(time / 3600)
        minutes = math.floor((time % 3600) / 60)
        seconds = math.floor(time % 60)

        return f"{hours:02d}h:{minutes:02d}m:{seconds:02d}s | (hh:mm:ss)"

    def _print_stats(self) -> None:
        print("\n-------------------------------------------------------------------")
        Logger.info("STATS", "Estadísticas de los crawlers:")
        for stat in self.stats:
            print("---------------------------------------")
            Logger.info("INFO", f"Site: {stat['site_name']}")
            Logger.info("INFO", f"Articles: {stat['articles']}")
            Logger.info("INFO", f"Time: {self._print_time(stat['time'])}")
        print("-------------------------------------------------------------------")

    def _save_articles(self, articles: List[Article]) -> None:
        print()
        if len(articles) == 0:
            Logger.info("INFO", "No se encontraron artículos")
            return

        try:
            folder_path = FileUtils.create_folder("newspapers")
            ExcelExporter.export(
                articles,
                f"newspapers_{self.date_range.start_date.strftime('%d-%m-%Y')}_to_{self.date_range.end_date.strftime('%d-%m-%Y')}.xlsx",
                folder_path,
            )
        except Exception as e:
            Logger.error("FILE", f"Error exporting articles to Excel: {e}")

        print("-------------------------------------------------------------------")
