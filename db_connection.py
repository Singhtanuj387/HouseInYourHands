import pymongo

url = 'mongodb://localhost:27017'
clint = pymongo.MongoClient(url)

db = clint['test_mongo']  