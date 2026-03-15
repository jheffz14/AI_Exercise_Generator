# youtube_uploader.py
"""
Upload a video to your YouTube channel using the YouTube Data API v3.

SETUP (do once):
  1. pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
  2. Create a project at https://console.cloud.google.com
  3. Enable "YouTube Data API v3"
  4. Create OAuth 2.0 credentials (Desktop App) → download as client_secrets.json
  5. Place client_secrets.json next to this file
  6. First run opens a browser to authorize — after that it's fully automatic

USAGE in main.py:
  from youtube_uploader import upload_to_youtube
  upload_to_youtube(
      video_path="output/20240101_FatBurn_1/fatburn_xxx.mp4",
      title="10 Minute Fat Burn Home Workout — No Equipment",
      description="Full body fat burn workout at home...",
      tags=["workout", "fatburn", "homeworkout", "noequipment", "fitness"],
  )
"""

import os
import pickle

SCOPES         = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_FILE     = "token.pickle"
SECRETS_FILE   = "client_secrets.json"
CATEGORY_ID    = "17"   # 17 = Sports
DEFAULT_PRIVACY = "public"  # "public" | "private" | "unlisted"


def _get_credentials():
    creds = None

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        from google.auth.transport.requests import Request
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            from google_auth_oauthlib.flow import InstalledAppFlow
            flow  = InstalledAppFlow.from_client_secrets_file(SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)

    return creds


def upload_to_youtube(
    video_path: str,
    title: str = "Fat Burn Home Workout",
    description: str = (
        "Full body fat burn workout at home — no equipment needed!\n\n"
        "💪 Body weight exercises only\n"
        "🔥 Burns maximum calories\n"
        "✅ Suitable for all fitness levels\n\n"
        "#workout #fatburn #homeworkout #noequipment #fitness #exercise"
    ),
    tags: list = None,
    privacy: str = DEFAULT_PRIVACY,
    made_for_kids: bool = False,
) -> str | None:
    """
    Upload video to YouTube. Returns the video URL or None on failure.

    Parameters
    ----------
    video_path   : path to the .mp4 file
    title        : YouTube video title
    description  : video description
    tags         : list of tag strings
    privacy      : "public", "private", or "unlisted"
    made_for_kids: set True if content is for children
    """
    if not os.path.exists(SECRETS_FILE):
        print(f"  ERROR: {SECRETS_FILE} not found.")
        print("  Download it from Google Cloud Console → Credentials → OAuth 2.0")
        return None

    if not os.path.exists(video_path):
        print(f"  ERROR: Video file not found: {video_path}")
        return None

    if tags is None:
        tags = ["workout", "fatburn", "homeworkout", "noequipment", "fitness",
                "exercise", "bodyweight", "cardio", "fatburning", "hiit"]

    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload

        print(f"\n  Uploading to YouTube: {os.path.basename(video_path)}")
        print(f"  Title: {title}")
        print(f"  Privacy: {privacy}")

        creds   = _get_credentials()
        youtube = build("youtube", "v3", credentials=creds)

        body = {
            "snippet": {
                "title":       title,
                "description": description,
                "tags":        tags,
                "categoryId":  CATEGORY_ID,
            },
            "status": {
                "privacyStatus":   privacy,
                "madeForKids":     made_for_kids,
                "selfDeclaredMadeForKids": made_for_kids,
            },
        }

        media = MediaFileUpload(
            video_path,
            mimetype="video/mp4",
            resumable=True,
            chunksize=1024 * 1024 * 5,   # 5 MB chunks
        )

        request  = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None

        print("  Uploading", end="", flush=True)
        while response is None:
            status, response = request.next_chunk()
            if status:
                pct = int(status.progress() * 100)
                print(f"\r  Uploading {pct}%", end="", flush=True)

        video_id = response.get("id")
        url      = f"https://www.youtube.com/watch?v={video_id}"
        print(f"\r  Uploaded!  {url}")
        return url

    except Exception as e:
        print(f"\n  YouTube upload failed: {e}")
        return None


if __name__ == "__main__":
    # Quick test — replace with your actual video path
    url = upload_to_youtube(
        video_path="output/test_video.mp4",
        title="Fat Burn Home Workout | No Equipment | 10 Minutes",
        privacy="private",   # start private for testing
    )
    if url:
        print("Success:", url)
