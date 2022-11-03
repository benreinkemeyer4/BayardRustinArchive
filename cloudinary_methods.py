import cloudinary
import cloudinary.uploader

cloudinary.config(
  cloud_name = "ddnep8fs3",
  api_key = "747566525248729",
  api_secret = "ygGyzq2xheDAfEd8v4dqttF4sro"
)
#CLOUDINARY_URL="//" + api_key + ":" + "api_secret" + "@" + cloud_name

def upload(file):
  upload_result = cloudinary.uploader.upload(file)
  return upload_result["secure_url"]