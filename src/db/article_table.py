from datetime import datetime
from typing import List

import pymongo

from core.models import Article
from db.mongo_connection import MongoConnection
from utils.logger import Logger


class ArticleTable:
    def __init__(self, mongodb_connection: MongoConnection):
        self.collection_name = "articles"

        collection_list = mongodb_connection.db.list_collection_names()
        if self.collection_name not in collection_list:
            mongodb_connection.db.create_collection(self.collection_name)
            mongodb_connection.db[self.collection_name].create_index([("url", 1)], unique=True)
            mongodb_connection.db[self.collection_name].create_index([("newspaper", 1), ("date", -1)])

        self.collection = mongodb_connection.db[self.collection_name]

    def save_articles(self, articles: List[Article]) -> None:
        try:
            BATCH_SIZE = 500
            operations = []

            articles_sorted = sorted(articles, key=lambda p: p.date or datetime.min)
            for article in articles_sorted:
                try:
                    document = {
                        "url": article.url,
                        "newspaper": article.newspaper.value,
                        "title": article.title,
                        "author": article.author,
                        "date": article.date,
                        "tag": article.tag,
                        "drophead": article.drophead,
                        "body": article.body,
                        "body_html": article.body_html,
                    }

                    operations.append(
                        pymongo.UpdateOne(
                            filter={"url": article.url},
                            update={"$set": document},
                            upsert=True,
                        )
                    )
                except Exception as e:
                    Logger.error("DB", f"Error al guardar el artículo: {article.url} [Error: {e}]")
                    continue

                if len(operations) == BATCH_SIZE:
                    self.collection.bulk_write(operations, ordered=False)
                    operations.clear()

            if len(operations) > 0:
                self.collection.bulk_write(operations, ordered=False)

            Logger.info("FILE", "Articles saved successfully to MongoDB")
        except Exception as e:
            Logger.error("DB", f"Error al guardar los artículos: {e}")

    def get_last_date_saved(self, newspaper_name: str) -> datetime | None:
        try:
            document = self.collection.find_one(
                {"newspaper": newspaper_name},
                sort=[("date", pymongo.DESCENDING)],
            )

            return document["date"] if document else None
        except Exception as e:
            Logger.error("DB", f"Error al obtener la fecha de guardado del último artículo guardado de {newspaper_name}: {e}")
            return None
