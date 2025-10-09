from services.crawler_service import CrawlerService

# ?: Definir los periodicos a ejecutar
CRAWLERS_TO_RUN = {
    # "ADN_RADIO": False,
    "COOPERATIVA": False,
    "EL_DESCONCIERTO": False,
    "EL_MOSTRADOR": False,
    "EMOL": False,
    "RADIO_UCHILE": False,
    "TVN_ACTUALIDAD": False,
    "TVN_NOTICIAS": False,
    # "CIPER": True,
}

# ?: FORMATO DE FECHAS: DD-MM-YYYY
START_DATE = "01-01-2020"
END_DATE = "30-06-2020"

# ?: Ejecutar el servicio
crawler_service = CrawlerService(START_DATE, END_DATE, CRAWLERS_TO_RUN)
crawler_service.run()
