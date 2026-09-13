# -*- coding: utf-8 -*-
"""موتور دانلود اپ اندروید (اجرا با Chaquopy) — نسخه بدون FFmpeg"""
import json
import os
import re
import glob
import yt_dlp

VERSION = "1.3"

YOUTUBE_HOSTS = ("youtube.com", "youtu.be", "music.youtube.com")
# ترتیب تلاش برای یوتیوب: پیش‌فرض، بعد کلاینت‌های مختلف
YOUTUBE_CLIENTS = [None, "android", "tv", "ios"]


def _qlabel(h):
    names = {
        2160: "2160p (4K)", 1440: "1440p (2K)", 1080: "1080p (Full HD)",
        720: "720p (HD)", 480: "480p", 360: "360p", 240: "240p", 144: "144p",
    }
    return names.get(h, "%sp" % h)


def _dur(s):
    if not s:
        return "—"
    s = int(s)
    h, r = divmod(s, 3600)
    m, s = divmod(r, 60)
    if h:
        return "%d:%02d:%02d" % (h, m, s)
    return "%d:%02d" % (m, s)


def _fmt_speed(bps):
    if not bps:
        return ""
    if bps >= 1024 * 1024:
        return "%.1f MB/s" % (bps / 1024.0 / 1024.0)
    if bps >= 1024:
        return "%d KB/s" % int(bps / 1024)
    return "%d B/s" % int(bps)


def _fmt_eta(e):
    if e is None:
        return ""
    e = int(e)
    m, s = divmod(e, 60)
    h, m = divmod(m, 60)
    if h:
        return "%d:%02d:%02d" % (h, m, s)
    return "%d:%02d" % (m, s)


def _report(listener, pct, extra):
    try:
        listener.onProgress(pct, extra)
    except Exception:
        try:
            listener.onProgress(pct)  # سازگاری با اپ‌های قدیمی
        except Exception:
            pass


def _safe_name(title, vid, ext, max_bytes=100):
    """اسم امن برای فایل: تمیز + کوتاه‌شده بر اساس بایت (نه حرف) تا خطای File name too long ندهد"""
    base = re.sub(r'[\\/*?:"<>|]', "", title or "").strip() or "video"
    base = base.encode("utf-8")[:max_bytes].decode("utf-8", "ignore").strip()
    if not base:
        base = "video"
    return "%s-%s.%s" % (base, vid, ext)


def _friendly(e):
    m = str(e).lower()
    if "unsupported url" in m:
        return "این لینک پشتیبانی نمی‌شود. لینک مستقیم صفحه ویدیو را بده."
    if "private" in m or "login required" in m or "log in" in m or "registered" in m:
        return "این ویدیو نیاز به ورود دارد. نسخه موبایل فقط ویدیوهای عمومی را پشتیبانی می‌کند."
    if "verification" in m or "verify your age" in m:
        return "این سایت احراز هویت می‌خواهد. با VPN امتحان کن."
    if "geo" in m or "not available in your country" in m:
        return "این ویدیو در منطقه تو بسته است. VPN بزن و دوباره تلاش کن."
    if "not available" in m or "unavailable" in m or "removed" in m or "deleted" in m:
        return "این ویدیو در دسترس نیست (حذف یا خصوصی شده)."
    if "timed out" in m or "timeout" in m or "network is unreachable" in m or "getaddrinfo" in m:
        return "مشکل اینترنت. اینترنت یا VPN را بررسی کن."
    if "bot" in m or "sign in to confirm" in m:
        return "یوتیوب گیر داده؛ کمی بعد دوباره تلاش کن."
    return "خطا: " + str(e)[:200]


def _is_youtube(url):
    u = (url or "").lower()
    return any(h in u for h in YOUTUBE_HOSTS)


def _opts(appdir, skip_dl, client=None):
    o = {"quiet": True, "no_warnings": True, "noplaylist": True,
         "socket_timeout": 25, "retries": 3}
    if skip_dl:
        o["skip_download"] = True
    if client:
        o["extractor_args"] = {"youtube": {"player_client": [client]}}
    c = os.path.join(appdir, "cookies.txt")
    if os.path.exists(c):
        o["cookiefile"] = c
    return o


def _extract(url, appdir, make_opts, want_download):
    """استخراج با تلاش چندمرحله‌ای (فقط یوتیوب چند کلاینت را امتحان می‌کند)"""
    clients = list(YOUTUBE_CLIENTS) if _is_youtube(url) else [None]
    last_err = Exception("unknown error")
    for client in clients:
        try:
            o = make_opts(client)
            with yt_dlp.YoutubeDL(o) as ydl:
                info = ydl.extract_info(url, download=want_download)
                if want_download:
                    try:
                        path = ydl.prepare_filename(info)
                    except Exception:
                        path = ""
                    return info, path
                return info, None
        except Exception as e:
            last_err = e
    raise last_err


def get_info(url, appdir):
    try:
        info, _ = _extract(url, appdir, lambda c: _opts(appdir, True, c), False)
        hs = set()
        for f in info.get("formats") or []:
            if f.get("vcodec") not in (None, "none") and f.get("height"):
                hs.add(int(f["height"]))
        qs = [{"id": "best", "label": "✨ بهترین کیفیت"}]
        for h in sorted(hs, reverse=True):
            qs.append({"id": str(h), "label": _qlabel(h)})
        return json.dumps({
            "ok": True,
            "title": info.get("title") or "بدون عنوان",
            "uploader": info.get("uploader") or info.get("channel") or "—",
            "duration": _dur(info.get("duration")),
            "thumbnail": info.get("thumbnail") or "",
            "qualities": qs,
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"ok": False, "error": _friendly(e),
                           "detail": str(e)[:300]}, ensure_ascii=False)


def download(url, quality, fmt, outdir, appdir, listener):
    def hook(d):
        try:
            if d.get("status") == "downloading":
                t = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                done = d.get("downloaded_bytes") or 0
                pct = int(done * 100 / t) if t else 0
                extra = _fmt_speed(d.get("speed"))
                eta = _fmt_eta(d.get("eta"))
                if eta:
                    extra = (extra + " ⏱ " + eta) if extra else ("⏱ " + eta)
                _report(listener, pct, extra)
            elif d.get("status") == "finished":
                _report(listener, 100, "")
        except Exception:
            pass

    def make_opts(client):
        o = _opts(appdir, False, client)
        # اسم موقت کوتاه (id) تا خطای File name too long نگیریم؛ بعداً rename می‌کنیم
        o["outtmpl"] = os.path.join(outdir, "%(id)s.%(ext)s")
        o["restrict_filenames"] = True
        o["progress_hooks"] = [hook]
        if fmt == "m4a":
            o["format"] = "bestaudio[ext=m4a]/bestaudio[ext=mp4]/bestaudio/best"
        elif quality == "best":
            o["format"] = "b[ext=mp4]/b"
        else:
            try:
                h = int(quality)
            except ValueError:
                h = 720
            o["format"] = "b[height<=%d][ext=mp4]/b[height<=%d]/b[ext=mp4]/b" % (h, h)
        return o

    try:
        info, path = _extract(url, appdir, make_opts, True)
        if not path or not os.path.exists(path):
            files = sorted(glob.glob(os.path.join(outdir, "*")), key=os.path.getmtime)
            path = files[-1] if files else ""
        if not path:
            return json.dumps({"ok": False, "error": "فایل دانلود شد ولی پیدا نشد!"})
        # تغییر اسم به عنوان ویدیو (کوتاه‌شده امن برای فایل‌سیستم)
        vid = (info.get("id") if info else "") or "video"
        ext = os.path.splitext(path)[1].lstrip(".") or ("m4a" if fmt == "m4a" else "mp4")
        title = (info.get("title") if info else "") or "video"
        new_path = os.path.join(outdir, _safe_name(title, vid, ext))
        try:
            if new_path != path:
                if os.path.exists(new_path):
                    os.remove(new_path)
                os.rename(path, new_path)
                path = new_path
        except OSError:
            pass  # اگه rename نشد، همون فایل id-based را تحویل بده
        return json.dumps({"ok": True, "path": path, "title": title}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"ok": False, "error": _friendly(e),
                           "detail": str(e)[:300]}, ensure_ascii=False)
