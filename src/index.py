import asyncio
import time

import yaml

from core.models import DateRange
from crawler.custom.cooperativa import CooperativaCrawler
from crawler.custom.tvn import TVNCrawler
from crawler.static_website import StaticWebsiteCrawler
from utils.logger import Logger

with open("src/crawler/_config.yaml", "r") as f:
    config = yaml.safe_load(f)

crawler_config = config.get("crawlers")[2]
date_range = DateRange(start_date="01-01-2023", end_date="31-12-2023")

if crawler_config.get("custom") is None:
    crawler = StaticWebsiteCrawler(crawler_config, date_range)
elif crawler_config.get("custom") == "TVN":
    crawler = TVNCrawler(crawler_config, date_range)
elif crawler_config.get("custom") == "COOPERATIVA":
    crawler = CooperativaCrawler(crawler_config, date_range)
else:
    raise ValueError("Custom crawler not supported")

start = time.time()
articles = asyncio.run(crawler.crawl())
end = time.time()

Logger.info(prefix="TIMER", message=f"Tiempo de ejecución: {(end - start):.2f} segundos")

print("------------------")
print(len(articles))
# print("------------------")
# print(articles[0])
# print("------------------")
# print(articles[-1])

# from utils.fetcher_manager import FetcherManager as FM
# import asyncio

# url = "https://www.elmostrador.cl/categoria/dia/page/1807/"
# html, status = asyncio.run(FM.async_fetch_html(url, retry_delay=5))
# print(html)

# from scrapling.fetchers import Fetcher
# url = "https://radio.uchile.cl/2023/01/04/carmen-romero-directora-de-santiago-a-mil-lo-que-queremos-que-la-gente-pueda-disfrutar-de-este-enero/"
# html = Fetcher.get(url, proxy="https://198.199.86.11:8080")
# # print(html.)
# elem = html.css_first(".post-header ul.meta li:last-child")
# # date = datetime.strptime(elem.get_all_text(), "%d-%m-%Y")
# print(elem)
