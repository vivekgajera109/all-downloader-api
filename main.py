from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
import logging
import requests
import re
import time
from bs4 import BeautifulSoup
import base64
import urllib.parse

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
def scrape_instagram(target_url: str):
    logger.info(f"Fallback scraper triggered for URL: {target_url}")
    try:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Sec-GPC": "1",
        })
        
        # 1. Fetch saveinsta.to highlights page to get tokens
        res = session.get("https://saveinsta.to/en/highlights", headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Referer": "https://www.google.com/",
        }, timeout=10)
        
        if res.status_code != 200:
            logger.error(f"Failed to fetch highlights page, status code: {res.status_code}")
            return None
            
        html = res.text
        script_match = re.search(r'<script[^>]*>var\s+k_url_search="[^"]+"(.*?)</script>', html, re.DOTALL)
        if not script_match:
            script_content = html
        else:
            script_content = script_match.group(1)
            
        k_exp_match = re.search(r'k_exp\s*=\s*"([^"]+)"', script_content)
        k_token_match = re.search(r'k_token\s*=\s*"([^"]+)"', script_content)
        
        if not k_exp_match or not k_token_match:
            k_exp_match = re.search(r'k_exp\s*=\s*"([^"]+)"', html)
            k_token_match = re.search(r'k_token\s*=\s*"([^"]+)"', html)
            
        if not k_exp_match or not k_token_match:
            logger.error("Could not extract k_exp or k_token")
            return None
            
        k_exp = k_exp_match.group(1)
        k_token = k_token_match.group(1)
        
        time.sleep(1)
        
        # 2. Get CF token (userverify)
        verify_url = "https://saveinsta.to/api/userverify"
        verify_headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://saveinsta.to",
            "Referer": "https://saveinsta.to/en/video",
            "X-Requested-With": "XMLHttpRequest"
        }
        
        verify_res = session.post(verify_url, data={"url": target_url}, headers=verify_headers, timeout=10)
        if verify_res.status_code != 200:
            logger.error(f"Failed to verify user, status code: {verify_res.status_code}")
            return None
            
        try:
            verify_data = verify_res.json()
        except Exception as e:
            logger.error(f"Failed to parse verify response: {e}")
            return None
            
        cftoken = verify_data.get("token")
        if not cftoken:
            logger.error("CF token not returned in JSON")
            return None
            
        time.sleep(1)
        
        # 3. Call ajaxSearch
        search_url = "https://saveinsta.to/api/ajaxSearch"
        search_headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://saveinsta.to",
            "Referer": "https://saveinsta.to/en/highlights",
            "X-Requested-With": "XMLHttpRequest"
        }
        
        search_data = {
            "k_exp": k_exp,
            "k_token": k_token,
            "q": target_url,
            "t": "media",
            "lang": "en",
            "v": "v2",
            "cftoken": cftoken
        }
        
        search_res = session.post(search_url, data=search_data, headers=search_headers, timeout=10)
        if search_res.status_code != 200:
            logger.error(f"ajaxSearch failed, status code: {search_res.status_code}")
            return None
            
        try:
            search_json = search_res.json()
        except Exception as e:
            logger.error(f"Failed to parse search response: {e}")
            return None
            
        if search_json.get("status") != "ok" or "data" not in search_json:
            logger.error("Invalid status or missing data in ajaxSearch response")
            return None
            
        html_data = search_json["data"]
        
        # 4. Parse HTML
        soup = BeautifulSoup(html_data, 'html.parser')
        
        videos = []
        for li in soup.select('ul.download-box li'):
            # Check thumbnail
            thumb_img = li.select_one('.download-items__thumb img')
            thumbnail = ""
            if thumb_img:
                thumbnail = thumb_img.get('data-src') or thumb_img.get('src') or ""
                if thumbnail == '/imgs/loader.gif':
                    thumbnail = thumb_img.get('data-src') or ""
            
            # Check buttons
            a_tags = li.select('.download-items__btn a')
            video_url = None
            for a in a_tags:
                if a.has_attr('video'):
                    video_url = a['video']
                    break
                text = a.text.lower()
                if 'download video' in text:
                    video_url = a.get('href')
                    break
                    
            if not video_url and a_tags:
                video_url = a_tags[0].get('href')
                
            if video_url:
                videos.append({
                    "url": video_url,
                    "thumbnail": thumbnail
                })
        
        return videos
    except Exception as e:
        logger.error(f"Scraper error: {e}")
        return None

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
        logger.warning(f"yt-dlp failed to fetch Instagram Reel ({str(e)}). Retrying with SaveInsta fallback scraper...")
        try:
            scraped_data = scrape_instagram(url)
            if scraped_data:
                logger.info(f"Fallback scraper successfully retrieved media content: {scraped_data}")
                return {
                    "url": {
                        "data": [
                            {
                                "url": item["url"],
                                "thumbnail": item["thumbnail"]
                            }
                            for item in scraped_data
                        ]
                    }
                }
        except Exception as fallback_err:
            logger.error(f"Fallback scraper also failed: {fallback_err}")
            
        logger.error(f"Instagram Fetch Error (both yt-dlp and fallback failed): {str(e)}")
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
def scrape_twitter_twitsave(tweet_url: str):
    logger.info(f"Fallback Twitter scraper triggered for URL: {tweet_url}")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        encoded_url = urllib.parse.quote(tweet_url, safe='')
        info_url = f"https://twitsave.com/info?url={encoded_url}"
        
        response = requests.get(info_url, headers=headers, timeout=10)
        if response.status_code != 200:
            logger.error(f"twitsave.com info endpoint failed: {response.status_code}")
            return None
            
        if "Sorry, we could not find any video on this tweet" in response.text:
            logger.warning("twitsave.com reported no video found in tweet")
            return None
            
        soup = BeautifulSoup(response.text, "html.parser")
        download_buttons = soup.find_all("a", href=True)
        
        links = []
        for btn in download_buttons:
            href = btn['href']
            text = btn.get_text(strip=True)
            if "download" in href or "download" in text.lower():
                links.append(href)
                
        resolved_links = []
        for l in links:
            if l.startswith("/"):
                resolved_links.append(f"https://twitsave.com{l}")
            else:
                resolved_links.append(l)
                
        filtered = [l for l in resolved_links if "twitsave.com" in l and "download" in l]
        if not filtered and resolved_links:
            filtered = resolved_links
            
        if filtered:
            target_url = filtered[0]
            try:
                parsed = urllib.parse.urlparse(target_url)
                params = urllib.parse.parse_qs(parsed.query)
                if 'file' in params:
                    encoded_file = params['file'][0]
                    missing_padding = len(encoded_file) % 4
                    if missing_padding:
                        encoded_file += '=' * (4 - missing_padding)
                    decoded_file = base64.b64decode(encoded_file).decode('utf-8')
                    logger.info(f"Successfully scraped and decoded Twitsave video URL: {decoded_file}")
                    return decoded_file
            except Exception as decode_err:
                logger.warning(f"Failed to decode Twitsave file parameter: {decode_err}")
                
            logger.info(f"Successfully scraped Twitsave video URL (undecoded): {target_url}")
            return target_url
            
        return None
    except Exception as e:
        logger.error(f"Twitsave scraper exception: {e}")
        return None

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
        logger.warning(f"yt-dlp failed to fetch Twitter/X Video ({str(e)}). Retrying with Twitsave fallback scraper...")
        try:
            fallback_url = scrape_twitter_twitsave(url)
            if fallback_url:
                logger.info(f"Fallback scraper successfully retrieved direct video URL: {fallback_url}")
                return {
                    "download_url": fallback_url
                }
        except Exception as fallback_err:
            logger.error(f"Fallback scraper also failed: {fallback_err}")
            
        logger.error(f"Twitter Fetch Error (both yt-dlp and fallback failed): {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch Twitter/X Video: {str(e)}")
