import asyncio
import logging
import time
import math

from services.excel_exporter import ExcelExporter
from spiders.cooperativa import Cooperativa
from spiders.el_desconcierto import ElDesconcierto
from spiders.el_mostrador import ElMostrador
from spiders.emol import Emol
from spiders.radio_uchile import RadioUChile
from spiders.tvn import Tvn
from utils.date_utils import DateUtils
from utils.file_utils import FileUtils


class ScraperRun:
    def __init__(self, start_date: str, end_date: str, spiders_to_run: dict):
        # Configure logging
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
        self.logger = logging.getLogger(__name__)
        
        # Validate dates
        try:
            start_date_dt = DateUtils.validate_date(start_date, "La fecha de inicio no es válida")
            end_date_dt = DateUtils.validate_date(end_date, "La fecha de fin no es válida")

            DateUtils.validate_date_range(start_date_dt, end_date_dt)

            # Set start and end dates
            self.start_date = start_date_dt
            self.end_date = end_date_dt
        except Exception as e:
            self.logger.error(e)
            exit(1)

        # Set spiders
        self.spiders = []
        all_spiders = [
            Cooperativa(),
            ElMostrador(),
            Emol(),
            Tvn(site_name="TVN_ACTUALIDAD", base_url="https://www.tvn.cl/noticias/actualidad"),
            Tvn(site_name="TVN_NOTICIAS", base_url="https://www.tvn.cl/noticias"),
            RadioUChile(),
            ElDesconcierto(),
        ]

        for spider in all_spiders:
            for key, value in spiders_to_run.items():
                if key == spider.SITE_NAME:
                    if value:
                        self.spiders.append(spider)

        # Initialize stats
        self.stats = []

    def run(self) -> None:
        self.papers = []
        for spider in self.spiders:
            start_time = time.time()
            spider_papers = asyncio.run(spider.run(self.start_date, self.end_date))
            end_time = time.time()
            self.logger.info(f"{spider.SITE_NAME}: {self._print_time(end_time - start_time)}")
            print("")

            self.stats.append({
                "SITE_NAME": spider.SITE_NAME,
                "PAPERS": len(spider_papers),
                "TIME": end_time - start_time
            })
            self.papers.extend(spider_papers)

        self._print_stats()
        self._save_papers()

    def _print_time(self, time: float) -> str:
        hours = math.floor(time / 3600)
        minutes = math.floor((time % 3600) / 60)
        seconds = math.floor(time % 60)

        return f"{hours:02d}h:{minutes:02d}m:{seconds:02d}s | (hh:mm:ss)"

    def _print_stats(self) -> None:
        print("")
        self.logger.info("-------------------------------------------------------------------")
        self.logger.info("Estadísticas de los spiders:")
        for stat in self.stats:
            self.logger.info("---------------------------------------")
            self.logger.info(f"\tSite: {stat['SITE_NAME']}")
            self.logger.info(f"\tPapers: {stat['PAPERS']}")
            self.logger.info(f"\tTiempo: {self._print_time(stat['TIME'])}")
        self.logger.info("---------------------------------------")

    def _save_papers(self) -> None:
        print("")
        self.logger.info("-------------------------------------------------------------------")
        if len(self.papers) == 0:
            self.logger.info("No se encontraron noticias.")
            return

        try:
            folder_path = FileUtils.create_folder("newspapers")
            ExcelExporter(self.papers, f"newspapers_{self.start_date.strftime('%d-%m-%Y')}_al_{self.end_date.strftime('%d-%m-%Y')}.xlsx", folder_path).export()
        except Exception as e:
            self.logger.error(e)
