import os
import time
import requests
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()

# Cloudinary config
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

# Instagram API creds
IG_USER_ID = os.getenv("IG_USER_ID")
ACCESS_TOKEN = os.getenv("IG_PAGE_ACCESS_TOKEN")


# ==========================
# CLOUDINARY + IG FUNCTIONS
# ==========================

def upload_to_cloudinary(local_video_path):
    print("☁ Uploading video to Cloudinary...")
    response = cloudinary.uploader.upload_large(
        local_video_path,
        resource_type="video"
    )

    video_url = response["secure_url"]
    print("☁ Cloudinary URL:", video_url)
    return video_url


def create_video_object(video_url, caption):
    print("🎬 Creating IG media object...")
    url = f"https://graph.facebook.com/v21.0/{IG_USER_ID}/media"

    params = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "access_token": ACCESS_TOKEN
    }

    response = requests.post(url, params=params).json()
    print("🎥 Media Object Response:", response)

    if "id" not in response:
        raise Exception(f"❌ Failed to create media object: {response}")

    return response["id"]


def check_media_status(creation_id):
    url = f"https://graph.facebook.com/v21.0/{creation_id}"
    params = {"fields": "status", "access_token": ACCESS_TOKEN}

    response = requests.get(url, params=params).json()
    print("⌛ Processing Status:", response)

    return response


def publish_video(creation_id):
    print("🚀 Publishing IG Reel...")
    url = f"https://graph.facebook.com/v21.0/{IG_USER_ID}/media_publish"
    params = {"creation_id": creation_id, "access_token": ACCESS_TOKEN}

    response = requests.post(url, params=params).json()
    print("📤 Publish Response:", response)

    if "id" not in response:
        raise Exception(f"❌ Failed to publish video: {response}")

    return response["id"]


# ==========================
# MAIN PUBLIC FUNCTION
# ==========================

def post_to_instagram(video_path, caption="Generated automatically ✨"):
    print(f"📤 Preparing to upload video: {video_path}")

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    # Step 1: Upload to Cloudinary
    video_url = upload_to_cloudinary(video_path)

    # Step 2: Create IG media upload object
    creation_id = create_video_object(video_url, caption)

    # Step 3: Poll IG processing status
    print("⏳ Waiting for Instagram to process video...")
    while True:
        status = check_media_status(creation_id)
        st = status.get("status", "")

        if "Finished" in st:
            print("✔ Processing complete!")
            break

        if "Error" in st:
            raise Exception(f"❌ Instagram processing error: {st}")

        time.sleep(3)

    # Step 4: Publish to Instagram
    post_id = publish_video(creation_id)
    print(f"✅ Reel posted! Post ID: {post_id}")
    print(f"👉 URL: https://instagram.com/p/{post_id}/")

    return post_id
