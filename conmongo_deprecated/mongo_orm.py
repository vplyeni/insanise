import pymongo

from conmongo.connection import mongodb
from mongo_model import mongo_model


class MongoORM:
    connection: pymongo.collection.Connection = None
    model: mongo_model = None

    def __init__(self, connection, model):
        self.connection = connection
        self.model = model
