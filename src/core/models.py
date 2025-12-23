from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Union


class SourceType(Enum):
    """Tipo de fuente de noticias"""

    API = "API"
    STATIC_WEB = "STATIC_WEB"
    DYNAMIC_WEB = "DYNAMIC_WEB"


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
    CIPER = "CIPER"


@dataclass
class DateRange:
    """Rango de fechas para filtrar artículos"""

    start_date: Union[str, datetime]
    end_date: Union[str, datetime]

    def __post_init__(self):
        # Convertir strings a datetime si es necesario
        if isinstance(self.start_date, str):
            try:
                self.start_date = datetime.strptime(self.start_date, "%d-%m-%Y")
            except ValueError as e:
                message = str(e)
                if "time data" and "does not match format" in message:
                    raise ValueError("La fecha de inicio debe tener el formato DD-MM-YYYY")
                else:
                    raise ValueError("La fecha de inicio es invalida")

        if isinstance(self.end_date, str):
            try:
                self.end_date = datetime.strptime(self.end_date, "%d-%m-%Y")
            except ValueError as e:
                message = str(e)
                if "time data" and "does not match format" in message:
                    raise ValueError("La fecha de fin debe tener el formato DD-MM-YYYY")
                else:
                    raise ValueError("La fecha de fin es invalida")

        # Obtener fecha actual
        current_date = datetime.now()

        # Validaciones
        if self.start_date > current_date:
            raise ValueError("La fecha de inicio debe ser anterior o igual a la fecha actual")

        if self.end_date > current_date:
            raise ValueError("La fecha de fin debe ser anterior o igual a la fecha actual")

        if self.start_date > self.end_date:
            raise ValueError("La fecha de inicio debe ser anterior o igual a la fecha de fin")


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
