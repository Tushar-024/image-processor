from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os

from utilities.dbConnection import dbConnectorClient
from processData import process_images
from celery import Celery

celery = Celery("tasks", broker="redis://localhost:6379/0")


BUCKET_NAME = "flask-testbucket1"


fileController_bp = Blueprint("fileController_bp", __name__)
import uuid


@fileController_bp.route("/upload", methods=["POST"])
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
            {"request_id": request_id, "status": "processing", "file_path": file_path}
        )

        process_images.delay(request_id)

        return jsonify({"request_id": request_id}), 202
    return jsonify({"error": "Invalid file type"}), 400


@fileController_bp.route("/status/<request_id>", methods=["GET"])
def get_status(request_id):
    client = dbConnectorClient()
    db = client["image_processing"]
    requests_collection = db["requests"]

    request_data = requests_collection.find_one({"_id": request_id})
    if request_data:
        return jsonify({"status": request_data["status"]}), 200
    return jsonify({"error": "Request not found"}), 404


def allowed_file(filename):
    allowed_extensions = {"csv", "xlsx"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


@fileController_bp.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    request_id = data.get("request_id")
    if request_id:
        # Update request status
        client = dbConnectorClient()
        db = client["image_processing"]
        requests_collection = db["requests"]

        requests_collection.update_one(
            {"_id": request_id}, {"$set": {"status": "webhook_triggered"}}
        )
        # Trigger your webhook logic here
        return jsonify({"message": "Webhook received and processed"}), 200
    return jsonify({"error": "Invalid webhook data"}), 400
