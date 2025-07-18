from services.scraper_run import ScraperRun

# Definicion de spiders a ejecutar
SPIDERS_TO_RUN = {
    "COOPERATIVA": True,
    "EL_MOSTRADOR": True,
    "EMOL": True,
    "TVN_NOTICIAS": True,
    "TVN_ACTUALIDAD": True
}

# Formato de fecha: dd-mm-yyyy
START_DATE = "01-01-2023"
END_DATE = "30-06-2023"

# Start System
ScraperRun(START_DATE, END_DATE, SPIDERS_TO_RUN).run()
