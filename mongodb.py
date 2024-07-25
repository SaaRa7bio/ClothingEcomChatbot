import csv

from bson import ObjectId
from pymongo import MongoClient
import pymongo

#connect database
client = MongoClient('mongodb://localhost:27017/')
db = client['MySmallBuisness']
collection = db['Products'] #the main dataset of the products


locations = db['locations'] #locations dataset for delivery details
dict_loc = locations.find_one({"cities": {"$exists": True}})

cities = dict_loc.get('cities')

#these below function will update stock availability when specific item is purchased or returned
def reduce_availability(db_name, collection_name, category, category_value, OptionNumber, OptionName, size, color):
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    collection = db[collection_name]

    query_filter = {f"categories.{category}": category_value, f"categories.options.{OptionNumber}": OptionName, "categories.options.sizes.size": size, "categories.options.sizes.colors.color": color}

    try:
        documents = collection.find(query_filter)
        for document in documents:
            availability = document["categories"][0]["options"][0]["sizes"][0]["colors"][0]["availability"]
            print(f"Before update: {availability}")

            # Update the availability
            availability -= 1
            collection.update_one({"_id": document["_id"]}, {"$set": {"categories.0.options.0.sizes.0.colors.0.availability": availability}})

            # Fetch the updated document
            updated_document = collection.find_one({"_id": document["_id"]})
            updated_availability = updated_document["categories"][0]["options"][0]["sizes"][0]["colors"][0]["availability"]
            print(f"Updated availability: {updated_availability}")
    except pymongo.errors.WriteError as e:
        print(f"Error: {e}")

    client.close()

def increment_availability(db_name, collection_name, category, category_value, OptionNumber, OptionName, size, color):
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    collection = db[collection_name]

    query_filter = {f"categories.{category}": category_value, f"categories.options.{OptionNumber}": OptionName, "categories.options.sizes.size": size, "categories.options.sizes.colors.color": color}

    try:
        documents = collection.find(query_filter)
        for document in documents:
            availability = document["categories"][0]["options"][0]["sizes"][0]["colors"][0]["availability"]
            print(f"Before update: {availability}")

            # Update the availability
            availability += 1
            collection.update_one({"_id": document["_id"]}, {"$set": {"categories.0.options.0.sizes.0.colors.0.availability": availability}})

            # Fetch the updated document
            updated_document = collection.find_one({"_id": document["_id"]})
            updated_availability = updated_document["categories"][0]["options"][0]["sizes"][0]["colors"][0]["availability"]
            print(f"Updated availability: {updated_availability}")
    except pymongo.errors.WriteError as e:
        print(f"Error: {e}")

    client.close()
