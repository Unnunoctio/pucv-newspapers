from pymongo import MongoClient

from utils.logger import Logger


class MongoConnection:
    def __init__(self, url: str, database: str):
        try:
            self.client = MongoClient(url)
            self.db = self.client[database]
            Logger.info("DB", f"Conectado a la base de datos MongoDB: {url}")
        except Exception as e:
            Logger.error("DB", f"Error al conectar a la base de datos MongoDB: {e}")
            exit(1)

    def close_connection(self) -> None:
        try:
            self.client.close()
            Logger.info("DB", "Conexión cerrada")
        except Exception as e:
            Logger.error("DB", f"Error al cerrar la conexión a la base de datos MongoDB: {e}")
