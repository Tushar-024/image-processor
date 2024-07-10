from bson.objectid import ObjectId

from utilities.dbConnection import dbConnectorClient


def save_request(csv_data):
    request = {"csv_data": csv_data, "status": "processing"}

    client = dbConnectorClient()
    db = client["image_processing"]
    collection = db["requests"]

    result = collection.insert_one(request)
    return str(result.inserted_id)


def get_status(request_id):

    client = dbConnectorClient()
    db = client["image_processing"]
    collection = db["requests"]

    request = collection.find_one({"_id": ObjectId(request_id)})
    if request:
        return {"status": request["status"], "data": request.get("data")}
    return None


def save_processed_images(request_id, processed_data):

    client = dbConnectorClient()
    db = client["image_processing"]
    collection = db["requests"]

    collection.update_one(
        {"_id": ObjectId(request_id)},
        {"$set": {"status": "completed", "data": processed_data}},
    )
    

