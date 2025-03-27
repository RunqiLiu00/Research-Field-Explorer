from pymongo import MongoClient
import pandas as pd

# widget 1 - trend of keywords: for a given keyword, return the number of publications related to the keyword over time.
def get_keyword_trend(keyword):
    # Making Connection
    myclient = MongoClient("mongodb://localhost:27017/")
    # database
    db = myclient["academicworld"]   
    # collection
    publication = db["publications"]

    query = [
        {"$match": {"keywords.name": keyword}},
        {"$group": {"_id": "$year", "n_publication": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    result = publication.aggregate(query)
    result_query = pd.DataFrame(list(result)).rename(
        columns={"_id": "year", "n_publication": "publication count"})
    
    # Filter data for years between 1980 and 2020
    filtered_data = result_query[(result_query['year'] >= 1980) & (result_query['year'] <= 2020)]
    
    return filtered_data



# get a list of all keywords
def get_keyword_list():
    # Making Connection
    myclient = MongoClient("mongodb://localhost:27017/")
    # database
    db = myclient["academicworld"]   
    # collection
    publication = db["publications"]
    keyword_list = publication.distinct("keywords.name")

    return keyword_list


