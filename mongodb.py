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
    client = MongoClient(mongodb_uri, tlsCAFile=certifi.where())
    db = client[db_name]
    collection = db[collection_name]

    try:
        documents = collection.find({
            f"categories.{category}": category_value,
            f"categories.options.{OptionNumber}": OptionName
        })

        for document in documents:
            for cat_index, cat in enumerate(document.get('categories', [])):
                if cat.get(category) == category_value:
                    for opt_index, opt in enumerate(cat.get('options', [])):
                        if opt.get(OptionNumber) == OptionName:
                            for sz_index, sz in enumerate(opt.get('sizes', [])):
                                if sz.get('size') == size:
                                    for col_index, col in enumerate(sz.get('colors', [])):
                                        if col.get('color') == color:
                                            # Update the availability
                                            collection.update_one(
                                                {"_id": document["_id"]},
                                                {"$inc": {
                                                    f"categories.{cat_index}.options.{opt_index}.sizes.{sz_index}.colors.{col_index}.availability": -1
                                                }}
                                            )
                                            print(f"Updated availability for document ID: {document['_id']}")
    except Exception as e:
        print(f"Error: {e}")

    finally:
        client.close()





def increment_availability(db_name, collection_name, category, category_value, OptionNumber, OptionName, size, color):
    client = MongoClient(mongodb_uri, tlsCAFile=certifi.where())
    db = client[db_name]
    collection = db[collection_name]

    try:
        documents = collection.find({
            f"categories.{category}": category_value,
            f"categories.options.{OptionNumber}": OptionName
        })

        for document in documents:
            for cat_index, cat in enumerate(document.get('categories', [])):
                if cat.get(category) == category_value:
                    for opt_index, opt in enumerate(cat.get('options', [])):
                        if opt.get(OptionNumber) == OptionName:
                            for sz_index, sz in enumerate(opt.get('sizes', [])):
                                if sz.get('size') == size:
                                    for col_index, col in enumerate(sz.get('colors', [])):
                                        if col.get('color') == color:
                                            # Update the availability
                                            collection.update_one(
                                                {"_id": document["_id"]},
                                                {"$inc": {
                                                    f"categories.{cat_index}.options.{opt_index}.sizes.{sz_index}.colors.{col_index}.availability": 1
                                                }}
                                            )
                                            print(f"Updated availability for document ID: {document['_id']}")
    except Exception as e:
        print(f"Error: {e}")

    finally:
        client.close()
