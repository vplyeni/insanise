import pymongo

# Define the connection parameters for pymongo
client = pymongo.MongoClient("mongodb://localhost:27017/")

# Access the specific database
db = client["insanise"]

task_user = db["task_user"]