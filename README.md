# ClipVerse Downloader API Backend

This is a premium, lightweight, and extremely stable multi-video downloader API built with **Python FastAPI** and **yt-dlp**.

It parses and extracts high-speed, direct video URLs from:
- **Instagram** (Posts and Reels)
- **Facebook** (HD and SD video streams)
- **Twitter / X** (Direct MP4 video URLs)

It matches the exact API response structures expected by the ClipVerse Flutter application.

---

## 🛠️ Local Setup and Run

### 1. Prerequisites
- **Python 3.8 or higher** installed on your system.

### 2. Create a Virtual Environment (Recommended)
Open your terminal in the `api_backend` directory:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# On Windows (Command Prompt):
.\venv\Scripts\activate.bat

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the API Server
```bash
uvicorn main:app --reload
```
The server will start running locally at: **`http://127.0.0.1:8000`**

---

## 🔍 How to Test the API

You can test the API endpoints using your browser or tools like Postman/thunder-client:

1. **API Status (Health Check)**
   - URL: `GET http://127.0.0.1:8000/`
   
2. **Instagram Reels & Posts**
   - URL: `GET http://127.0.0.1:8000/igdl?url={INSTAGRAM_REEL_OR_POST_URL}`
   
3. **Facebook Videos**
   - URL: `GET http://127.0.0.1:8000/fb?url={FACEBOOK_VIDEO_URL}`
   
4. **Twitter / X Videos**
   - URL: `POST http://127.0.0.1:8000/twitter`
   - Headers: `Content-Type: application/json`
   - JSON Body:
     ```json
     {
       "url": "https://x.com/username/status/1234567890"
     }
     ```

---

## 🚀 Deployment to Render.com (Free Hosting)

To make your API accessible worldwide and plug it into your production Flutter app, deploy it to Render:

1. Create a free account on [Render.com](https://render.com/).
2. Push this `api_backend` code to a repository on **GitHub** or **GitLab**.
3. On Render Dashboard, click **New +** and select **Web Service**.
4. Connect your Git Repository.
5. Configure the service:
   - **Name**: `clipverse-downloader-api`
   - **Environment / Runtime**: `Python`
   - **Branch**: `main` (or your active branch)
   - **Build Command**: `pip install -r requirements.txt` (Render automatically detects this)
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Click **Deploy Web Service**.
7. Once deployed, Render will provide you with a URL (e.g., `https://clipverse-downloader-api.onrender.com`).

---

## 📲 Integrating with your Flutter App

After deploying, update your Flutter provider URLs:

1. **Instagram Reels / Posts & Facebook** ([insta_reels_provider.dart](file:///d:/My%20PRoject/all-video-downloader_25-12/lib/provider/insta_reels_provider.dart), [insta_post_provider.dart](file:///d:/My%20PRoject/all-video-downloader_25-12/lib/provider/insta_post_provider.dart), [fb_video_provider.dart](file:///d:/My%20PRoject/all-video-downloader_25-12/lib/provider/fb_video_provider.dart)):
   - Replace `https://instagram-video-downloader-api-main.onrender.com` with `https://your-deployed-app.onrender.com`
2. **Twitter/X** ([twitter_provider.dart](file:///d:/My%20PRoject/all-video-downloader_25-12/lib/provider/twitter_provider.dart)):
   - Replace `https://twdownloader-v1.onrender.com/twitter` with `https://your-deployed-app.onrender.com/twitter`
