import logging
import os
from collections import defaultdict
from datetime import datetime

from openpyxl import Workbook

from classes.paper import Paper


class ExcelExporter:
    def __init__(self, papers: list[Paper], file_name: str, folder_path: str):
        self.papers = papers
        self.file_name = file_name
        self.folder_path = folder_path
        self.file_path = os.path.join(folder_path, file_name)

        # Configure logging
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
        self.logger = logging.getLogger(__name__)

    def group_by_newspaper(self):
        grouped = defaultdict(list)
        for paper in self.papers:
            newspaper = paper.newspaper or "UNKNOWN"
            grouped[newspaper].append(paper)

        return grouped

    def export(self):
        wb = Workbook()
        grouped_papers = self.group_by_newspaper()

        for i, (newspaper, papers) in enumerate(grouped_papers.items()):
            ws = wb.create_sheet(title=newspaper) if i != 0 else wb.active
            ws.title = newspaper

            ws.append(["Newspaper", "URL", "Autor/Autores", "Fecha", "Tag", "Título", "Bajada", "Resumen", "Cuerpo", "Cuerpo HTML"])

            papers_sorted = sorted(papers, key=lambda p: p.date or datetime.min)
            for paper in papers_sorted:
                ws.append([paper.newspaper, paper.url, paper.author or "", paper.date.strftime("%d-%m-%Y") if paper.date else "", paper.tag or "", paper.title or "", paper.drophead or "", paper.excerpt or "", paper.body or "", paper.bodyHTML or ""])

        try:
            wb.save(self.file_path)
            self.logger.info(f"Archivo exportado a {self.file_path}")
        except Exception as e:
            self.logger.error(f"Error al exportar el archivo Excel: {e}")
