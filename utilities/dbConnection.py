import os

import certifi
from dotenv import load_dotenv
from flask import jsonify
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

load_dotenv()


def dbConnectorClient():
    try:
        # uri = "mongodb+srv://tusharsingla:KKDzdqOzIhAd32ln@cluster0.77xqmrf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        uri = os.getenv("MONGO_URI")
        client = MongoClient(uri, tlsCAFile=certifi.where())
        print("Connected to MongoDB")

        return client
    except ConnectionFailure:
        print("Connection to MongoDB failed.")
        return (
            jsonify(
                {
                    "data": None,
                    "statusCode": 500,
                    "errorMessage": "Connection to MongoDB failed.",
                    "errorCode": 500,
                }
            ),
            500,
        )
