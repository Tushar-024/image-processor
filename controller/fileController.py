from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from service.fileProcessorService import upload_file , get_status
from celery import Celery






fileController_bp = Blueprint("fileController_bp", __name__)


@fileController_bp.route("/upload", methods=["POST"])
def upload_file_service():
    return upload_file()


@fileController_bp.route("/status/<request_id>", methods=["GET"])
def get_status_service(request_id):
    return get_status(request_id)




# @fileController_bp.route("/webhook", methods=["POST"])
# def webhook():
#     data = request.json
#     request_id = data.get("request_id")
#     if request_id:
#         # Update request status
#         client = dbConnectorClient()
#         db = client["image_processing"]
#         requests_collection = db["requests"]

#         requests_collection.update_one(
#             {"_id": request_id}, {"$set": {"status": "webhook_triggered"}}
#         )
#         # Trigger your webhook logic here
#         return jsonify({"message": "Webhook received and processed"}), 200
#     return jsonify({"error": "Invalid webhook data"}), 400
