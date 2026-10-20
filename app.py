import os, re
from urllib.parse import quote, unquote, urlparse
import requests, yt_dlp
from flask import Flask, jsonify, request, Response, abort
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
# Set ALLOWED_ORIGIN to your site, e.g. https://yourdomain.com (use * only for testing)
CORS(app, origins=os.getenv("ALLOWED_ORIGIN", "*"))
limiter = Limiter(get_remote_address, app=app, default_limits=["60 per hour", "10 per minute"])

IG_RE = re.compile(r"^https?://(www\.)?instagram\.com/(reel|reels|p|tv)/[\w-]+", re.I)
CDN_OK = (".cdninstagram.com", ".fbcdn.net")  # only these hosts can be proxied
COOKIES = os.getenv("IG_COOKIES")  # optional path to cookies.txt (helps when Instagram blocks)


@app.get("/")
def health():
    return {"status": "ok"}


@app.get("/api/info")
def info():
    link = request.args.get("url", "").strip()
    kind = request.args.get("type", "video")
    if not IG_RE.match(link):
        return jsonify(error="Invalid Instagram link"), 400
    opts = {
        "quiet": True, "skip_download": True, "noplaylist": True,
        "format": "bestaudio/best" if kind == "audio" else "best[ext=mp4]/best",
    }
    if COOKIES and os.path.exists(COOKIES):
        opts["cookiefile"] = COOKIES
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            d = ydl.extract_info(link, download=False)
    except Exception:
        return jsonify(error="Could not fetch. Reel may be private or blocked."), 502
    src = d.get("url")
    if not src:
        return jsonify(error="No downloadable file found"), 404
    ext = "m4a" if kind == "audio" else "mp4"
    title = (d.get("title") or "reel")[:60]
    h = d.get("height")
    name = re.sub(r"[^\w\- ]", "", title).strip() or "reel"
    proxy = f"{request.host_url}api/file?u={quote(src, safe='')}&n={quote(name)}.{ext}"
    return jsonify(title=title, quality=f"{h}p" if h else "HD", url=proxy)


@app.get("/api/file")
def file():
    u = unquote(request.args.get("u", ""))
    p = urlparse(u)
    if p.scheme != "https" or not (p.hostname or "").endswith(CDN_OK):
        abort(400)
    name = re.sub(r"[^\w.\- ]", "", request.args.get("n", "reel.mp4")) or "reel.mp4"
    r = requests.get(u, stream=True, timeout=15, allow_redirects=False)
    if r.status_code != 200:
        abort(502)
    headers = {"Content-Disposition": f'attachment; filename="{name}"'}
    if r.headers.get("Content-Length"):
        headers["Content-Length"] = r.headers["Content-Length"]
    return Response(r.iter_content(65536), content_type=r.headers.get("Content-Type", "video/mp4"), headers=headers)


if __name__ == "__main__":
    app.run(port=int(os.getenv("PORT", 5000)))
