#pip install cloudinary
import cloudinary
import cloudinary.uploader
import cloudinary.api

cloudinary.config( 
  cloud_name = "ddnep8fs3", 
  api_key = "747566525248729", 
  api_secret = "ygGyzq2xheDAfEd8v4dqttF4sro" 
)
#CLOUDINARY_URL="//" + api_key + ":" + "api_secret" + "@" + cloud_name

def upload(file):
  cloudinary.uploader.upload(file)
  return cloudinary.CloudinaryImage(str(file)).build_url()


