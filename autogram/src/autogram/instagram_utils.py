import os
import time
import requests
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

IG_USER_ID = os.getenv("IG_USER_ID")
ACCESS_TOKEN = os.getenv("IG_PAGE_ACCESS_TOKEN")


def upload_video_to_cloudinary(path):
    r = cloudinary.uploader.upload_large(path, resource_type="video")
    return r["secure_url"]


def create_media(video_url, caption):
    url = f"https://graph.facebook.com/v21.0/{IG_USER_ID}/media"
    params = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "access_token": ACCESS_TOKEN
    }
    r = requests.post(url, params=params).json()
    if "id" not in r:
        raise Exception("Media creation failed", r)
    return r["id"]


def wait_for_processing(media_id):
    while True:
        url = f"https://graph.facebook.com/v21.0/{media_id}"
        params = {"fields": "status", "access_token": ACCESS_TOKEN}
        r = requests.get(url, params=params).json()
        status = r.get("status", "")
        if "Finished" in status:
            return
        if "Error" in status:
            raise Exception("Processing failed", status)
        time.sleep(3)


def publish_media(media_id):
    url = f"https://graph.facebook.com/v21.0/{IG_USER_ID}/media_publish"
    params = {"creation_id": media_id, "access_token": ACCESS_TOKEN}
    r = requests.post(url, params=params).json()
    if "id" not in r:
        raise Exception("Publish failed", r)
    return r["id"]


def post_to_instagram(video_path, caption):
    video_url = upload_video_to_cloudinary(video_path)
    media_id = create_media(video_url, caption)
    wait_for_processing(media_id)
    post_id = publish_media(media_id)
    return post_id
