# tiktok_uploader.py
"""
Upload a video to TikTok using browser automation (tiktok-uploader library).

This is the easiest working method for personal channels since TikTok's
official Content Posting API requires business/developer approval.

SETUP (do once):
  1. pip install tiktok-uploader
  2. Install Chrome: https://www.google.com/chrome
  3. Install ChromeDriver matching your Chrome version:
       https://googlechromelabs.github.io/chrome-for-testing/
       Place chromedriver.exe (Windows) or chromedriver (Mac/Linux) in your PATH
       OR in the same folder as this file
  4. Run this file once — it will open Chrome and ask you to log in to TikTok
  5. After login, your session cookies are saved automatically

USAGE in main.py:
  from tiktok_uploader import upload_to_tiktok
  upload_to_tiktok(
      video_path="output/20240101_FatBurn_1/fatburn_xxx.mp4",
      title="10 Min Fat Burn Home Workout No Equipment",
      tags=["fatburn", "homeworkout", "workout", "fitness", "noequipment"],
  )

NOTE: TikTok may update their site and break browser automation.
      If it stops working, use the Creator Studio website manually:
      https://www.tiktok.com/creator-center/upload
"""

import os

COOKIES_FILE = "tiktok_cookies.json"


def upload_to_tiktok(
    video_path: str,
    title: str = "Fat Burn Home Workout 🔥 No Equipment",
    tags: list = None,
    headless: bool = False,   # set True to hide the browser window
) -> bool:
    """
    Upload video to TikTok. Returns True on success, False on failure.

    Parameters
    ----------
    video_path : path to the .mp4 file
    title      : caption/description for the TikTok post (max 2200 chars)
    tags       : list of hashtags (without #)
    headless   : run browser in background (True) or visible (False)
    """
    if not os.path.exists(video_path):
        print(f"  ERROR: Video not found: {video_path}")
        return False

    if tags is None:
        tags = ["fatburn", "homeworkout", "workout", "fitness",
                "noequipment", "bodyweight", "cardio", "exercise"]

    # Build caption with hashtags
    hashtags = " ".join(f"#{t.strip('#')}" for t in tags)
    caption  = f"{title} {hashtags}"

    try:
        from tiktok_uploader.upload import upload_video

        print(f"\n  Uploading to TikTok: {os.path.basename(video_path)}")
        print(f"  Caption: {caption[:80]}...")

        # First run: no cookies yet → opens browser for manual login
        result = upload_video(
            filename=video_path,
            description=caption,
            cookies=COOKIES_FILE if os.path.exists(COOKIES_FILE) else None,
            headless=headless,
        )

        if result:
            print("  TikTok upload successful!")
            return True
        else:
            print("  TikTok upload returned no result — check the browser window.")
            return False

    except ImportError:
        print("  ERROR: tiktok-uploader not installed.")
        print("  Run:  pip install tiktok-uploader")
        return False
    except Exception as e:
        print(f"  TikTok upload failed: {e}")
        print("  Try running with headless=False to see what happened in the browser.")
        return False


def save_tiktok_cookies():
    """
    Open a browser window for you to log in manually.
    Saves the session cookies so future uploads are automatic.
    """
    try:
        from tiktok_uploader.auth import AuthBackend
        auth = AuthBackend(cookies=COOKIES_FILE)
        auth.authenticate_with_tiktok()
        print(f"  Cookies saved to {COOKIES_FILE}")
    except Exception as e:
        print(f"  Cookie save failed: {e}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "login":
        print("Opening browser for TikTok login ...")
        save_tiktok_cookies()
    else:
        # Test upload
        path = input("Video path to test upload: ").strip()
        upload_to_tiktok(
            video_path=path,
            title="Fat Burn Home Workout 🔥 No Equipment Needed",
            headless=False,
        )
