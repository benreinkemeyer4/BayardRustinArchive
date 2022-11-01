#pip install cloudinary
import cloudinary
import cloudinary.uploader
import cloudinary.api

cloudinary.config( 
  cloud_name = "ddnep8fs3", 
  api_key = "747566525248729", 
  api_secret = "ygGyzq2xheDAfEd8v4dqttF4sro" 
)

def upload(file):
  # upload file to cloudinary
  uploaded_file = cloudinary.uploader.upload(file)

  # delete file from local env

  return uploaded_file['url']


