import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import os

cloudinary.config(
  cloud_name = os.environ.get("cloud_name"),
  api_key = os.environ.get("api_key"),
  api_secret = os.environ.get("api_secret")
)

""" cloudinary.config(
  cloud_name = "ddnep8fs3",
  api_key = "747566525248729",
  api_secret = "ygGyzq2xheDAfEd8v4dqttF4sro"
)
 """

def upload(file):
  upload_result = cloudinary.uploader.upload(file)
  return upload_result["secure_url"]