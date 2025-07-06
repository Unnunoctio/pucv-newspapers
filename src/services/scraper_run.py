import logging

from services.excel_exporter import ExcelExporter
from spiders.cooperativa import Cooperativa
from utils.date_utils import DateUtils
from utils.file_utils import FileUtils


class ScraperRun:
    def __init__(self, start_date: str, end_date: str, spiders_to_run: dict):
        # Configure logging
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
        self.logger = logging.getLogger(__name__)

        # Validate dates
        self._validate_dates(start_date, end_date)

        # Set spiders
        self._set_spiders(spiders_to_run)

    def _validate_dates(self, start_date: str, end_date: str) -> None:
        try:
            start_date_dt = DateUtils.validate_date(start_date, "La fecha de inicio no es válida")
            end_date_dt = DateUtils.validate_date(end_date, "La fecha de fin no es válida")

            DateUtils.validate_date_range(start_date_dt, end_date_dt)

            # Set start and end dates
            self.start_date = start_date_dt
            self.end_date = end_date_dt
        except Exception as e:
            self.logger.error(e)
            return

    def _set_spiders(self, spiders_to_run: dict) -> None:
        self.spiders = []
        all_spiders = [Cooperativa()]

        for spider in all_spiders:
            for key, value in spiders_to_run.items():
                if key == spider.SITE_NAME:
                    if value:
                        self.spiders.append(spider)

    def run(self) -> None:
        self.papers = []
        for spider in self.spiders:
            spider_papers = spider.run(self.start_date, self.end_date)
            self.papers.extend(spider_papers)

        self._print_stats()
        self._save_papers()

    def _print_stats(self) -> None:
        print("")
        self.logger.info("-------------------------------------------------------------------")
        self.logger.info("Cantidad total de noticias obtenidas:")
        for spider in self.spiders:
            papers_by_site = [p for p in self.papers if p.newspaper == spider.SITE_NAME]
            self.logger.info(f"{spider.SITE_NAME}: {len(papers_by_site)}")

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
