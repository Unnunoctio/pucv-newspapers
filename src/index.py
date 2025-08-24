from services.scraper_run import ScraperRun

# Definicion de spiders a ejecutar
SPIDERS_TO_RUN = {
    "COOPERATIVA": True,
    "EL_MOSTRADOR": False,
    "EMOL": False,
    "TVN_NOTICIAS": False,
    "TVN_ACTUALIDAD": False,
    "RADIO_UCHILE": False,
    "EL_DESCONCIERTO": False,
    # "ADN_RADIO": False,
}

# Formato de fecha: dd-mm-yyyy
START_DATE = "01-01-2023"
END_DATE = "31-03-2023"

# Start System
ScraperRun(START_DATE, END_DATE, SPIDERS_TO_RUN).run()
