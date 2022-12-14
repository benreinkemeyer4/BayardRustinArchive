import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import os
import sys


cloudinary.config(
  cloud_name = os.environ.get("cloud_name"),
  api_key = os.environ.get("api_key"),
  api_secret = os.environ.get("api_secret")
)

def upload(file):
  try:
    upload_result = cloudinary.uploader.upload(file)
    return {"result": upload_result["secure_url"], "error":False}
  except Exception as ex:
    print(f"{sys.argv[0]}: {ex}", file=sys.stderr)
    return {"result": "Cloudinary Error", "error":True}
