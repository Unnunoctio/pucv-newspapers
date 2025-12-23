from datetime import datetime, timedelta

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from db.article_table import ArticleTable
from db.mongo_connection import MongoConnection
from services.crawler_service import CrawlerService
from services.data_storage import DataStorage

# ?: Definir los periodicos a ejecutar
CRAWLERS_TO_RUN = {
    "COOPERATIVA": False,
    "EL_DESCONCIERTO": False,
    "EL_MOSTRADOR": False,
    "EMOL": False,
    "RADIO_UCHILE": False,
    "TVN_ACTUALIDAD": True,
    "TVN_NOTICIAS": True,
    "CIPER": False,
}

IS_MANUAL = False

if IS_MANUAL:
    # ?: FORMATO DE FECHAS: DD-MM-YYYY
    START_DATE = "01-01-2025"
    END_DATE = "15-10-2025"

    # ?: Ejecutar el servicio
    CrawlerService(START_DATE, END_DATE, CRAWLERS_TO_RUN).run(data_storage=DataStorage("EXCEL"))
else:
    # ?: MONGODB DATABASE URL & COLLECTION NAME
    MONGO_URI = "mongodb://localhost:27017"  # Your MongoDB connection string
    MONGO_DATABASE = "newspapers"

    # ?: CRON SCHEDULE DEFINITION
    CRON_SCHEDULE = "0 8 * * *"  # 8:00 AM every day, url for create your own schedule: https://crontab.cronhub.io/

    # TODO: ESTO DEBE ESTAR DENTRO DEL CRON
    def run_crawler():
        mongodb_connection = MongoConnection(MONGO_URI, MONGO_DATABASE)
        articles_table = ArticleTable(mongodb_connection)

        for key, value in CRAWLERS_TO_RUN.items():  # Por cada newspaper activo obtiene su ultima fecha guardada y ejecuta el crawler para solo ese newspaper
            if value is False:
                continue

            last_date_saved = articles_table.get_last_date_saved(key)
            START_DATE = last_date_saved if last_date_saved else datetime.strptime("01-01-2000", "%d-%m-%Y")
            END_DATE = datetime.now()

            TOTAL_DAYS = (END_DATE - START_DATE).days

            # ? En caso que el rango de dias sea mayor a un año, se ejecutará el crawler en bloques de 365 días, con el fin de evitar utilizar mucha memoria e i
            for offset in range(0, TOTAL_DAYS, 365):
                batch_start_date = START_DATE + timedelta(days=offset)
                batch_end_date = min(batch_start_date + timedelta(days=365), END_DATE)

                # Logger.info("INFO", f"Crawling newspaper {key} from {batch_start_date.strftime('%d-%m-%Y')} to {batch_end_date.strftime('%d-%m-%Y')}")
                CrawlerService(batch_start_date.strftime("%d-%m-%Y"), batch_end_date.strftime("%d-%m-%Y"), {key: True}).run(data_storage=DataStorage("MONGO_DB", articles_table))

                if key == "TVN_ACTUALIDAD" or key == "TVN_NOTICIAS":  # TVN_ACTUALIDAD y NOTICIAS No siguen la logica de rangos de dias, por lo que solo se ejecuta una vez
                    break

        mongodb_connection.close_connection()

    scheduler = BlockingScheduler()
    trigger = CronTrigger.from_crontab(CRON_SCHEDULE)
    scheduler.add_job(run_crawler, trigger)
    scheduler.start()
