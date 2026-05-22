from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
import logging

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ClipVerse Multi-Downloader API",
    description="Python FastAPI backend powered by yt-dlp to download media from Instagram, Facebook, and Twitter/X.",
    version="1.0.0"
)

# Add CORS Middleware to allow requests from any client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for Twitter POST requests
class TwitterRequest(BaseModel):
    url: str

@app.get("/")
def home():
    return {
        "status": "online",
        "service": "ClipVerse Downloader API",
        "supported_platforms": ["Instagram Reels/Post", "Facebook Video", "Twitter/X Video"]
    }

# =====================================================================
# 📸 INSTAGRAM ENDPOINT (Supports both Reels and Posts)
# =====================================================================
@app.get("/igdl")
def get_instagram_video(url: str = Query(..., description="Instagram video or post URL")):
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    logger.info(f"Fetching Instagram URL: {url}")

    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        # Set User-Agent to match standard web browsers to prevent rate limiting
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Handle list/playlist response if multiple slides exist
            if 'entries' in info:
                entry = info['entries'][0]
                video_url = entry.get('url')
                thumbnail = entry.get('thumbnail')
            else:
                video_url = info.get('url')
                thumbnail = info.get('thumbnail')

            if not video_url:
                raise HTTPException(status_code=404, detail="Could not extract video URL")

            # Return response in the exact JSON structure expected by the Flutter app
            return {
                "url": {
                    "data": [
                        {
                            "url": video_url,
                            "thumbnail": thumbnail or ""
                        }
                    ]
                }
            }
    except Exception as e:
        logger.error(f"Instagram Fetch Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch Instagram Reel: {str(e)}")

# =====================================================================
# 👥 FACEBOOK ENDPOINT
# =====================================================================
@app.get("/fb")
def get_facebook_video(url: str = Query(..., description="Facebook video URL")):
    if not url:
        return {"success": False, "msg": "URL is required"}

    logger.info(f"Fetching Facebook URL: {url}")

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            
            hd_url = None
            sd_url = None
            
            # Extract HD and SD quality video URLs
            for f in formats:
                format_id = f.get('format_id', '')
                url_candidate = f.get('url')
                
                # Check height resolution for quality grouping
                height = f.get('height') or 0
                if 'hd' in format_id or height >= 720:
                    if not hd_url:
                        hd_url = url_candidate
                elif 'sd' in format_id or (0 < height < 720):
                    if not sd_url:
                        sd_url = url_candidate

            # Fallbacks if one quality is not explicitly marked
            if not hd_url and not sd_url:
                sd_url = info.get('url')
                hd_url = sd_url
            elif not hd_url:
                hd_url = sd_url
            elif not sd_url:
                sd_url = hd_url

            if not hd_url:
                raise Exception("No video streams found")

            # Return response in the exact structure expected by fb_video_provider.dart
            return {
                "success": True,
                "hd": hd_url,
                "sd": sd_url
            }
    except Exception as e:
        logger.error(f"Facebook Fetch Error: {str(e)}")
        return {
            "success": False,
            "msg": f"Failed to fetch Facebook Video: {str(e)}"
        }

# =====================================================================
# 🐦 TWITTER / X ENDPOINT
# =====================================================================
@app.post("/twitter")
def get_twitter_video(request: TwitterRequest):
    url = request.url
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    logger.info(f"Fetching Twitter URL: {url}")

    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url')
            
            if not video_url:
                raise Exception("Could not find direct video URL")

            # Return response in the structure expected by twitter_provider.dart
            return {
                "download_url": video_url
            }
    except Exception as e:
        logger.error(f"Twitter Fetch Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch Twitter/X Video: {str(e)}")
