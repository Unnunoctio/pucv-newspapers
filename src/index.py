from services.scraper_run import ScraperRun

# Definicion de spiders a ejecutar
SPIDERS_TO_RUN = {
    "COOPERATIVA": True,
    "EL_MOSTRADOR": False,
    "EMOL": False,
    "TVN": False
}

# Formato de fecha: dd-mm-yyyy
START_DATE = "05-07-2025"
END_DATE = "05-07-2025"

# Start System
ScraperRun(START_DATE, END_DATE, SPIDERS_TO_RUN).run()


