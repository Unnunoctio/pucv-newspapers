from typing import List, Dict, Any


class StaticWebSource:
    """Clase base para todas las fuentes de noticias que son de tipo web estático"""

    def __init__(self, config: Dict[str, Any]):
        self.SITE_NAME = config.get("site_name", "unknown")
        self.URLS = config.get("url", [])
        

    