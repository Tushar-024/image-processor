import uuid
from flask import request, jsonify
from werkzeug.utils import secure_filename
import os

from utilities.dbConnection import dbConnectorClient
from processData import process_images
from celery import Celery
from datetime import datetime

celery = Celery("tasks", broker=os.getenv("REDIS_URL"))


def upload_file():

    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):

        client = dbConnectorClient()
        db = client[os.getenv("MONGODB_DATABASE")]
        requests_collection = db[os.getenv("MONGODB_REQUESTS_COLLECTION")]

        filename = secure_filename(file.filename)
        file_path = os.path.join("temp_uploads", filename)
        file.save(file_path)

        request_id = str(uuid.uuid4())
        requests_collection.insert_one(
            {
                "request_id": request_id,
                "status": "processing",
                "file_path": file_path,
                "created_at": datetime.now(),
            }
        )

        process_images.delay(request_id)

        return (
            jsonify(
                {
                    "request_id": request_id,
                    "created_at": datetime.now(),
                    "status": "processing",
                }
            ),
            202,
        )
    return (
        jsonify(
            {
                "error": "Invalid file type",
                "status": "failed",
            }
        ),
        400,
    )


def get_status(request_id):
    client = dbConnectorClient()
    db = client["image_processing"]
    requests_collection = db["requests"]

    request_data = requests_collection.find_one({"request_id": request_id})
    if request_data:
        return jsonify({"status": request_data["status"]}), 200
    return jsonify({"error": "Request not found"}), 404


def allowed_file(filename):
    allowed_extensions = {"csv", "xlsx"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions
