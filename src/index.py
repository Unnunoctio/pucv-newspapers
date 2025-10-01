from services.crawler_service import CrawlerService

# ?: Definir los periodicos a ejecutar
CRAWLERS_TO_RUN = {
    # "ADN_RADIO": False,
    "COOPERATIVA": True,
    "EL_DESCONCIERTO": True,
    "EL_MOSTRADOR": True,
    # "EMOL": False,
    "RADIO_UCHILE": True,
    "TVN_ACTUALIDAD": True,
    "TVN_NOTICIAS": True,
}

# ?: FORMATO DE FECHAS: DD-MM-YYYY
START_DATE = "01-01-2016"
END_DATE = "31-01-2016"

# ?: Ejecutar el servicio
crawler_service = CrawlerService(START_DATE, END_DATE, CRAWLERS_TO_RUN)
crawler_service.run()

#! TEST
# import asyncio

# import yaml
# from bs4 import BeautifulSoup

# from core.models import DateRange
# from crawlers.generics.static_website import StaticWebsiteCrawler
# from utils.logger import Logger

# with open("src/config.yaml", "r") as f:
#     data = yaml.safe_load(f)

# crawler_config = data.get("crawlers")[3]
# crawler = StaticWebsiteCrawler(crawler_config, DateRange("01-01-2019", "31-12-2019"))

# url = "https://radio.uchile.cl/2019/01/17/diputado-pablo-vidal-y-tpp-11-lo-mas-probable-es-que-este-tratado-sea-aprobado/"
# html, status = asyncio.run(crawler.FETCHER.fetch_html(url=url))

# soup = BeautifulSoup(html, "html.parser")

# title = soup.select_one("div.post-header h1.title").get_text(strip=True)
# print(title)

# article = crawler._parse_article(html, url)
# if article.date is None:
#     Logger.error("DB", f"No se ha podido obtener los datos de la noticia: {url}")
# print(article)

# asyncio.run(crawler.FETCHER.close())


