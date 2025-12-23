from typing import List

from core.models import Article, DateRange
from db.article_table import ArticleTable
from services.excel_exporter import ExcelExporter
from utils.file_utils import FileUtils
from utils.logger import Logger


class DataStorage:
    def __init__(self, storage_mode: str, db_table: ArticleTable | None = None):
        if storage_mode not in ["EXCEL", "MONGO_DB"]:
            Logger.error("STORAGE", f"Storage mode [{storage_mode}] not supported")
            exit(1)

        self.storage_mode = storage_mode

        self.db_table = db_table

    async def save_articles(self, articles: List[Article], date_range: DateRange) -> None:
        if self.storage_mode == "EXCEL":
            self._save_articles_to_excel(articles, date_range)
        elif self.storage_mode == "MONGO_DB":
            self._save_articles_to_mongo(articles)

    def _save_articles_to_excel(self, articles: List[Article], date_range: DateRange) -> None:
        print()
        if len(articles) == 0:
            Logger.info("INFO", "No se encontraron artículos")
            return

        try:
            folder_path = FileUtils.create_folder("newspapers")
            ExcelExporter.export(
                articles,
                f"newspapers_{date_range.start_date.strftime('%d-%m-%Y')}_to_{date_range.end_date.strftime('%d-%m-%Y')}.xlsx",
                folder_path,
            )
        except Exception as e:
            Logger.error("FILE", f"Error exporting articles to Excel: {e}")

        print("-------------------------------------------------------------------")

    def _save_articles_to_mongo(self, articles: List[Article]) -> None:
        print()
        if self.db_table is None:
            Logger.error("DB", "No se ha podido conectar a la base de datos")
            return

        if len(articles) == 0:
            Logger.info("INFO", "No se encontraron artículos")
            return

        try:
            self.db_table.save_articles(articles)
        except Exception as e:
            Logger.error("DB", f"Error al guardar los artículos en la base de datos: {e}")

        print("-------------------------------------------------------------------")
