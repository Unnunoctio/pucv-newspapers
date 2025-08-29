from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class SourceType(Enum):
    """Tipo de fuente de noticias"""

    API = "api"
    STATIC_WEB = "static_web"
    DYNAMIC_WEB = "dynamic_web"


class NewspaperType(Enum):
    """Tipo de periódico"""

    COOPERATIVA = "COOPERATIVA"
    EL_MOSTRADOR = "EL_MOSTRADOR"
    EMOL = "EMOL"
    TVN_NOTICIAS = "TVN_NOTICIAS"
    TVN_ACTUALIDAD = "TVN_ACTUALIDAD"
    RADIO_UCHILE = "RADIO_UCHILE"
    EL_DESCONCIERTO = "EL_DESCONCIERTO"
    ADN_RADIO = "ADN_RADIO"


@dataclass
class DateRange:
    """Rango de fechas para filtrar artículos"""

    start_date: datetime
    end_date: datetime

    def __post_init__(self):
        try:
            datetime.strptime(self.start_date, "%d-%m-%Y")
            datetime.strptime(self.end_date, "%d-%m-%Y")
        except ValueError:
            raise ValueError("Las fechas deben tener el formato DD-MM-YYYY")

        current_date = datetime.now()
        if self.start_date > current_date:
            raise ValueError(
                "La fecha de inicio debe ser anterior o igual a la fecha actual"
            )
        if self.end_date > current_date:
            raise ValueError(
                "La fecha de fin debe ser anterior o igual a la fecha actual"
            )
        if self.start_date > self.end_date:
            raise ValueError(
                "La fecha de inicio debe ser anterior o igual a la fecha de fin"
            )


@dataclass
class Article:
    """Representa un artículo de una fuente de noticias"""

    newspaper: NewspaperType
    url: str  # URL completa del artículo
    title: Optional[str] = None  # Título del artículo
    author: Optional[str] = None  # Autor del artículo
    date: Optional[datetime] = None  # Fecha de publicación del artículo
    tag: Optional[str] = None  # Etiqueta del artículo
    drophead: Optional[str] = None  # Cabecera del artículo
    body: Optional[str] = None  # Cuerpo del artículo
    body_html: Optional[str] = None  # Cuerpo del artículo en HTML

    def __post_init__(self):
        pass
