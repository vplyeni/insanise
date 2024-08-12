
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
mongodb = client['insanise']

mongo_field = mongodb['Field']

mongo_task = mongodb['Task']
