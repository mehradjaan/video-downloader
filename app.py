# -*- coding: utf-8 -*-
"""
🎬 ویدیو دانلودر — وب‌اپ دانلود ویدیو از ۱۰۰۰+ سایت (یوتیوب، اینستاگرام، تیک‌تاک، آپارات و...)
اجرا:
    pip install -r requirements.txt
    python app.py
بعد مرورگر را باز کن: http://localhost:5000
👨‍💻 برنامه‌نویس: مهراد چناقچی | IG: mehrad_chenaghchi_1990
"""
from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os
import re
import glob
import time
import shutil
import uuid
import threading
import subprocess
import sys

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# نگهداری نام اصلی فایل‌ها برای دانلود با اسم قشنگ
FILE_NAMES = {}

# سایت‌هایی که راهنمای مخصوص می‌خوان (فیلتر/VPN/ورود)
ADULT_HINT_SITES = ("pornhub", "xvideos", "xhamster", "xnxx", "redtube",
                    "youporn", "spankbang", "xhamsterlive")

ADULT_HINT = ("💡 راهنمای این سایت: ۱) همین لینک را در مرورگر خودت باز کن — اگر باز نشد (فیلتر است)، "
              "VPN بزن، چون برنامه از اینترنت خود گوشی/کامپیوترت استفاده می‌کند. "
              "۲) بعضی ویدیوها فقط برای کاربران واردشده است — در ویندوز از «تنظیمات پیشرفته» مرورگری که با آن وارد شدی را انتخاب کن. "
              "۳) یک ویدیوی دیگر را هم امتحان کن.")

ALLOWED_BROWSERS = ("chrome", "firefox", "edge", "brave", "opera", "vivaldi", "chromium")


def base_opts():
    """آپشن‌های پایه yt-dlp"""
    opts = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,      # فقط همان یک ویدیو، نه کل پلی‌لیست
        "socket_timeout": 25,
        "retries": 3,
    }
    # اگر فایل cookies.txt کنار برنامه باشه (برای ویدیوهای نیازمند ورود)، استفاده می‌شه
    cookies = os.path.join(BASE_DIR, "cookies.txt")
    if os.path.exists(cookies):
        opts["cookiefile"] = cookies
    return opts


def apply_browser_cookies(opts, data):
    """اگر کاربر مرورگر انتخاب کرده، کوکی‌ها را از همان مرورگر بخوان (فقط دسکتاپ)"""
    b = (data.get("browser") or "").strip().lower()
    if b in ALLOWED_BROWSERS:
        opts["cookiesfrombrowser"] = (b, None, None, None)


def format_duration(seconds):
    if not seconds:
        return "—"
    seconds = int(seconds)
    h, r = divmod(seconds, 3600)
    m, s = divmod(r, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def quality_label(h):
    names = {
        2160: "2160p (4K کیفیت فوق‌العاده)",
        1440: "1440p (2K)",
        1080: "1080p (Full HD)",
        720: "720p (HD)",
        480: "480p",
        360: "360p",
        240: "240p",
        144: "144p",
    }
    return names.get(h, f"{h}p")


def friendly_error(e, url=""):
    """ترجمه خطاهای رایج yt-dlp به فارسی ساده"""
    msg = str(e).lower()
    is_adult = any(s in (url or "").lower() for s in ADULT_HINT_SITES)

    if "could not find" in msg and ("browser" in msg or "cookies" in msg):
        base = "مرورگر انتخاب‌شده روی این دستگاه پیدا نشد. مطمئن شو روی همین دستگاه نصب است (این گزینه روی اندروید کار نمی‌کند)."
    elif "failed to extract cookies" in msg or "could not extract cookies" in msg or ("keyring" in msg and "cookie" in msg):
        base = "خواندن کوکی از مرورگر ناموفق بود. مرورگر را کامل ببند و دوباره تلاش کن."
    elif "unsupported url" in msg:
        base = "این لینک پشتیبانی نمی‌شود. مطمئن شو لینک مستقیم صفحه ویدیو است (نه صفحه اصلی سایت یا پروفایل)."
    elif "private" in msg:
        base = "این ویدیو خصوصی است و بدون ورود به حساب قابل دانلود نیست."
    elif "login required" in msg or "log in" in msg or "registered" in msg:
        base = "این ویدیو نیاز به ورود دارد. در ویندوز از «تنظیمات پیشرفته» مرورگری که با آن وارد شدی را انتخاب کن، یا فایل cookies.txt بساز."
    elif "verification" in msg or "verify your age" in msg:
        base = "این سایت احراز سن/هویت می‌خواهد. با VPN امتحان کن یا در مرورگر وارد حسابت شو و گزینه «کوکی مرورگر» را انتخاب کن."
    elif "geo" in msg or "not available in your country" in msg or "blocked in your country" in msg:
        base = "این ویدیو در کشور/منطقه تو بسته است. VPN بزن و دوباره تلاش کن."
    elif "age" in msg and ("confirm" in msg or "gate" in msg):
        base = "این ویدیو محدودیت سنی دارد و نیاز به ورود (کوکی مرورگر یا cookies.txt) دارد."
    elif "not available" in msg or "unavailable" in msg or "removed" in msg or "deleted" in msg or "not found" in msg:
        base = "این ویدیو در دسترس نیست (حذف یا خصوصی شده است). یک ویدیوی دیگر را امتحان کن."
    elif "timed out" in msg or "timeout" in msg:
        base = "اتصال طول کشید. اینترنت یا VPN را بررسی کن و دوباره تلاش کن."
    elif "name resolution" in msg or "getaddrinfo" in msg or "network is unreachable" in msg:
        base = "مشکل اتصال به اینترنت. اینترنت یا VPN را بررسی کن."
    elif "ffmpeg" in msg:
        base = "خطای FFmpeg. مطمئن شو FFmpeg نصب است (راهنما را ببین)."
    elif "sign in to confirm" in msg or "bot" in msg:
        base = "یوتیوب درخواست ورود کرد. کمی بعد تلاش کن یا گزینه «کوکی مرورگر» را انتخاب کن."
    else:
        base = f"خطا: {str(e)[:250]}"

    if is_adult:
        base = base + " " + ADULT_HINT
    return base


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status")
def api_status():
    """وضعیت سرور: نصب بودن FFmpeg و نسخه yt-dlp"""
    try:
        ver = yt_dlp.version.__version__
    except Exception:
        ver = "نامشخص"
    return jsonify({
        "ok": True,
        "ffmpeg": shutil.which("ffmpeg") is not None,
        "ytdlp_version": ver,
    })


@app.route("/api/update", methods=["POST"])
def api_update():
    """آپدیت موتور دانلود (yt-dlp) به آخرین نسخه"""
    try:
        old_ver = yt_dlp.version.__version__
    except Exception:
        old_ver = "نامشخص"
    try:
        r = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-U", "yt-dlp"],
            capture_output=True, text=True, timeout=240
        )
        if r.returncode != 0:
            err = (r.stderr or r.stdout or "").strip()[-400:]
            return jsonify({"ok": False, "error": f"آپدیت ناموفق بود. اینترنت را بررسی کن و دوباره تلاش کن. ({err})"})
        try:
            from importlib.metadata import version as pkg_version
            new_ver = pkg_version("yt-dlp")
        except Exception:
            new_ver = old_ver

        def _norm(v):
            # یکسان‌سازی فرمت نسخه‌ها: 2026.08.19 و 2026.8.19 یکی هستند
            return ".".join((p.lstrip("0") or "0") for p in str(v).split("."))

        if _norm(new_ver) == _norm(old_ver):
            return jsonify({
                "ok": True, "changed": False, "old": old_ver, "new": new_ver,
                "message": f"قبلاً به‌روزی! نسخه فعلی موتور: {old_ver} ✅",
            })
        return jsonify({
            "ok": True, "changed": True, "old": old_ver, "new": new_ver,
            "message": f"آپدیت شد: {old_ver} ← {new_ver} 🎉 حالا برنامه را ری‌استارت کن (ببند و دوباره اجرا کن) تا نسخه جدید لود شود.",
        })
    except subprocess.TimeoutExpired:
        return jsonify({"ok": False, "error": "آپدیت طول کشید و متوقف شد. اینترنت را بررسی کن و دوباره تلاش کن."})
    except Exception as e:
        return jsonify({"ok": False, "error": f"خطا در آپدیت: {str(e)[:200]}"})


@app.route("/api/info", methods=["POST"])
def api_info():
    """گرفتن مشخصات ویدیو + لیست کیفیت‌ها"""
    data = request.get_json(force=True, silent=True) or {}
    url = (data.get("url") or "").strip()

    if not url or not url.lower().startswith(("http://", "https://")):
        return jsonify({"ok": False, "error": "لطفاً یک لینک معتبر وارد کن (باید با http شروع شود)."})

    try:
        opts = base_opts()
        opts["skip_download"] = True
        apply_browser_cookies(opts, data)
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as e:
        return jsonify({"ok": False, "error": friendly_error(e, url)})

    # استخراج کیفیت‌های موجود
    heights = set()
    has_video = False
    for f in info.get("formats") or []:
        if f.get("vcodec") not in (None, "none"):
            has_video = True
            h = f.get("height")
            if h:
                heights.add(int(h))

    qualities = [{"id": "best", "label": "✨ بهترین کیفیت"}]
    for h in sorted(heights, reverse=True):
        qualities.append({"id": str(h), "label": quality_label(h)})

    return jsonify({
        "ok": True,
        "title": info.get("title") or "بدون عنوان",
        "uploader": info.get("uploader") or info.get("channel") or "—",
        "duration": format_duration(info.get("duration")),
        "thumbnail": info.get("thumbnail") or "",
        "site": info.get("extractor_key") or info.get("extractor") or "",
        "qualities": qualities,
        "has_video": has_video,
    })


@app.route("/api/download", methods=["POST"])
def api_download():
    """دانلود ویدیو در سرور و آماده‌سازی برای تحویل به مرورگر"""
    data = request.get_json(force=True, silent=True) or {}
    url = (data.get("url") or "").strip()
    quality = (data.get("quality") or "best").strip()
    fmt = (data.get("format") or "mp4").strip().lower()

    if not url or not url.lower().startswith(("http://", "https://")):
        return jsonify({"ok": False, "error": "لینک معتبر نیست."})
    if fmt not in ("mp4", "mp3"):
        return jsonify({"ok": False, "error": "فرمت باید mp4 یا mp3 باشد."})

    has_ffmpeg = shutil.which("ffmpeg") is not None
    if fmt == "mp3" and not has_ffmpeg:
        return jsonify({"ok": False, "error": "برای خروجی MP3 باید FFmpeg نصب باشد. (در ویندوز/ترماکس طبق راهنما نصبش کن، یا فعلاً MP4 بگیر.)"})

    uid = uuid.uuid4().hex[:12]
    outtmpl = os.path.join(DOWNLOAD_DIR, f"{uid}.%(ext)s")

    opts = base_opts()
    opts["outtmpl"] = outtmpl
    opts["restrict_filenames"] = True
    apply_browser_cookies(opts, data)

    if fmt == "mp3":
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
    else:
        if has_ffmpeg:
            # با FFmpeg: بهترین تصویر + بهترین صدا ترکیب می‌شن (بهترین کیفیت واقعی)
            if quality == "best":
                opts["format"] = "bv*+ba/b"
            else:
                try:
                    h = int(quality)
                except ValueError:
                    h = 720
                opts["format"] = f"bv*[height<={h}]+ba/b[height<={h}]/b"
            opts["merge_output_format"] = "mp4"
        else:
            # بدون FFmpeg: تک‌فایل (بدون نیاز به ترکیب)
            if quality == "best":
                opts["format"] = "b[ext=mp4]/b"
            else:
                try:
                    h = int(quality)
                except ValueError:
                    h = 720
                opts["format"] = f"b[height<={h}][ext=mp4]/b[height<={h}]/b[ext=mp4]/b"

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            dl_info = ydl.extract_info(url, download=True)
    except Exception as e:
        return jsonify({"ok": False, "error": friendly_error(e, url)})

    matches = glob.glob(os.path.join(DOWNLOAD_DIR, uid + ".*"))
    if not matches:
        return jsonify({"ok": False, "error": "فایل دانلود شد ولی پیدا نشد! دوباره تلاش کن."})

    path = matches[0]
    ext = os.path.splitext(path)[1].lstrip(".") or fmt
    raw_title = (dl_info.get("title") if dl_info else "") or "video"
    safe_title = re.sub(r'[\\/*?:"<>|]', "", raw_title).strip()[:80] or "video"
    filename = f"{safe_title}.{ext}"
    FILE_NAMES[uid] = filename

    return jsonify({
        "ok": True,
        "file_id": uid,
        "filename": filename,
        "title": raw_title,
    })


@app.route("/file/<fid>")
def serve_file(fid):
    if not re.fullmatch(r"[a-f0-9]{12}", fid or ""):
        return "پیدا نشد.", 404
    matches = glob.glob(os.path.join(DOWNLOAD_DIR, fid + ".*"))
    if not matches:
        return "فایل پیدا نشد یا منقضی شده. دوباره دانلود کن.", 404
    path = matches[0]
    name = FILE_NAMES.get(fid, os.path.basename(path))
    return send_file(path, as_attachment=True, download_name=name)


def cleanup_loop():
    """پاک‌سازی خودکار فایل‌های قدیمی‌تر از ۲ ساعت، هر ۱۰ دقیقه"""
    while True:
        time.sleep(600)
        now = time.time()
        for f in glob.glob(os.path.join(DOWNLOAD_DIR, "*")):
            try:
                if now - os.path.getmtime(f) > 7200:
                    os.remove(f)
            except OSError:
                pass


if __name__ == "__main__":
    t = threading.Thread(target=cleanup_loop, daemon=True)
    t.start()
    print("=" * 50)
    print("🎬 ویدیو دانلودر اجرا شد!")
    print("🌐 مرورگر را باز کن و برو به:  http://localhost:5000")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000)
