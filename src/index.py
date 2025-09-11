from services.scraper_run import ScraperRun

# Definicion de spiders a ejecutar
SPIDERS_TO_RUN = {
    "COOPERATIVA": False,
    "EL_MOSTRADOR": False,
    "EMOL": False,
    "TVN_NOTICIAS": False,
    "TVN_ACTUALIDAD": False,
    "RADIO_UCHILE": False,
    "EL_DESCONCIERTO": False,
    "ADN_RADIO": True,
}

# Formato de fecha: dd-mm-yyyy
START_DATE = "01-04-2025"
END_DATE = "30-04-2025"

# Start System
ScraperRun(START_DATE, END_DATE, SPIDERS_TO_RUN).run()
