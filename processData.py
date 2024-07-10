import os
from celery import Celery
import csv
import requests
from PIL import Image
from io import BytesIO
from utilities.dbConnection import dbConnectorClient
import pandas as pd
import boto3


celery = Celery("tasks", broker="redis://localhost:6379/0")

BUCKET_NAME = os.getenv("BUCKET_NAME")


@celery.task
def process_images(request_id):
    try:
        client = dbConnectorClient()
        db = client[os.getenv("MONGODB_DATABASE")]
        requests_collection = db[os.getenv("MONGODB_REQUESTS_COLLECTION")]
        products_collection = db[os.getenv("MONGODB_PRODUCTS_COLLECTION")]

        request_data = requests_collection.find_one({"request_id": request_id})

        file_path = request_data["file_path"]
        file_extension = file_path.split(".")[-1].lower()

        print("Processing images")

        if file_extension == "csv":
            df = pd.read_csv(file_path)
        elif file_extension == "xlsx":
            df = pd.read_excel(file_path)
        else:
            raise ValueError(
                "Unsupported file format. Only CSV and XLSX are supported."
            )

        for index, row in df.iterrows():
            serial_no = row["Serial Number"]
            product_name = row["Product Name"]
            print(f"Processing images for {product_name}")
            input_urls = row["Input Image Urls"].split(",")
            print("input URLs", input_urls)
            output_urls = []

            for url_index, url in enumerate(input_urls):
                try:
                    # Download image
                    response = requests.get(url.strip())
                    response.raise_for_status()
                    img = Image.open(BytesIO(response.content))

                    # Compress image
                    output = BytesIO()
                    img.save(output, format="JPEG", quality=50)
                    output.seek(0)

                    # Upload to S3
                    filename = f"{product_name}_{url_index}.jpeg"
                    s3 = boto3.client(
                        "s3",
                        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                    )

                    s3.upload_fileobj(output, BUCKET_NAME, filename)

                    output_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{filename}"
                    print("output_url", output_url)
                    output_urls.append(output_url)

                    print("all output done ")
                except requests.RequestException as e:
                    print(f"Failed to download image from {url}: {e}")
                except Exception as e:
                    print(f"Failed to process image from {url}: {e}")

            product_data = products_collection.find_one({"request_id": request_id})
            if product_data:
                for item in product_data["data"]:
                    if item["serial_no"] == serial_no:
                        item["input_urls"] = input_urls
                        item["output_urls"] = output_urls
                        break
                else:
                    product_data["data"].append(
                        {
                            "serial_no": serial_no,
                            "product_name": product_name,
                            "input_urls": input_urls,
                            "output_urls": output_urls,
                        }
                    )
                products_collection.replace_one(
                    {"request_id": request_id}, product_data
                )
            else:
                products_collection.insert_one(
                    {
                        "request_id": request_id,
                        "data": [
                            {
                                "serial_no": serial_no,
                                "product_name": product_name,
                                "input_urls": input_urls,
                                "output_urls": output_urls,
                            }
                        ],
                    }
                )

        response = requests_collection.update_one(
            {"request_id": request_id},
            {
                "$set": {
                    "status": "completed",
                }
            },
        )

        print("response update request", response.modified_count)
    except Exception as e:
        print(f"Failed to process images: {e}")
        requests_collection.update_one(
            {"request_id": request_id},
            {
                "$set": {
                    "status": "failed",
                    "error": str(e),
                }
            },
        )
    finally:
        client.close()
