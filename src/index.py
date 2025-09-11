import asyncio

import yaml

from core.models import DateRange
from crawler.custom.cooperativa import CooperativaCrawler
from crawler.custom.tvn import TVNCrawler
from crawler.static_website import StaticWebsiteCrawler

with open("src/crawler/_config.yaml", "r") as f:
    config = yaml.safe_load(f)

crawler_config = config.get("crawlers")[4]
date_range = DateRange(start_date="01-01-2023", end_date="31-12-2023")

if crawler_config.get("custom") is None:
    crawler = StaticWebsiteCrawler(crawler_config, date_range)
elif crawler_config.get("custom") == "TVN":
    crawler = TVNCrawler(crawler_config, date_range)
elif crawler_config.get("custom") == "COOPERATIVA":
    crawler = CooperativaCrawler(crawler_config, date_range)
else:
    raise ValueError("Custom crawler not supported")

articles = asyncio.run(crawler.crawl())

print(len(articles))
