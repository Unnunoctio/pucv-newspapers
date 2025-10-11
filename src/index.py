from services.crawler_service import CrawlerService

# ?: Definir los periodicos a ejecutar
CRAWLERS_TO_RUN = {
    # "ADN_RADIO": False,
    "COOPERATIVA": True,
    "EL_DESCONCIERTO": True,
    "EL_MOSTRADOR": True,
    "EMOL": True,
    "RADIO_UCHILE": True,
    "TVN_ACTUALIDAD": True,
    "TVN_NOTICIAS": True,
    "CIPER": True,
}

# ?: FORMATO DE FECHAS: DD-MM-YYYY
START_DATE = "09-10-2025"
END_DATE = "10-10-2025"

# ?: Ejecutar el servicio
crawler_service = CrawlerService(START_DATE, END_DATE, CRAWLERS_TO_RUN)
crawler_service.run()

# Variaciones
# - 
