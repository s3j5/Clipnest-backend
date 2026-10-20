# ClipNest Backend

## Run locally
    pip install -r requirements.txt
    python app.py
Test: http://localhost:5000/api/info?url=https://www.instagram.com/reel/XXXX/

## Deploy on Render (free)
1. Upload this folder to a GitHub repo.
2. Render.com -> New -> Web Service -> pick the repo.
3. Build command: pip install -r requirements.txt
4. Start command: gunicorn app:app
5. Env var: ALLOWED_ORIGIN = your website URL.
6. Copy the Render URL, then in index.html set:
   var API_URL = "https://YOUR-APP.onrender.com/api/info";

## Keep yt-dlp updated
Instagram changes often. Redeploy regularly (pip install -U yt-dlp).

## If Instagram blocks requests
Export cookies.txt from a spare account, set env IG_COOKIES to its path.
Datacenter IPs get blocked often; a VPS with a residential-friendly IP works better.
