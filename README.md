# 🎬 ویدیو دانلودر — وب‌اپ پایتون (ویندوز + اندروید)

لینک ویدیو را می‌دهی، مشخصات و کیفیت‌ها را می‌بینی، فرمت **MP4 (ویدیو)** یا **MP3 (صدا)** را انتخاب می‌کنی و دانلود می‌کنی.
با موتور **yt-dlp** از بیش از **۱۰۰۰ سایت** پشتیبانی می‌کند: یوتیوب، اینستاگرام (ریلز/پست)، تیک‌تاک، آپارات، توییتر/X و...

⭐ اگه به کارت اومد، به ریپو **ستاره (Star)** بده! 😉

---

## 📁 فایل‌های پروژه

| فایل | توضیح |
|---|---|
| `app.py` | کد اصلی برنامه (Flask) |
| `templates/index.html` | رابط کاربری فارسی و موبایل‌فرندلی |
| `requirements.txt` | کتابخانه‌های لازم |
| `run-windows.bat` | اجرای سریع در ویندوز (دابل‌کلیک) |
| `setup-termux.sh` | ستاپ ترموکس: ساخت دستور `vd` و شورتکات ویجت |
| `termux-oneliner.txt` | تک‌خط نصب خودکار در ترموکس |
| `downloads/` | پوشه دانلودهای موقت (خودکار ساخته می‌شود) |

---

## 🪟 اجرا روی ویندوز

1. **پایتون را نصب کن** (اگر نداری): از [python.org](https://www.python.org/downloads/) نسخه 3.10 به بالا. موقع نصب حتماً تیک **Add python.exe to PATH** را بزن.
2. از صفحه [**Releases**](https://github.com/mehradjaan/video-downloader/releases) فایل `VideoDownloader-Windows.zip` را دانلود و باز کن (یا همین ریپو را Clone/دانلود کن).
3. روی فایل **`run-windows.bat` دابل‌کلیک کن**. (همه‌چیز خودش نصب و اجرا می‌شود ✅)
   - روش دستی: باز کردن CMD داخل پوشه و اجرای این دو دستور:
     ```
     pip install -r requirements.txt
     python app.py
     ```
4. مرورگر را باز کن و برو به: **http://localhost:5000**

### نصب FFmpeg در ویندوز (برای MP3 و بهترین کیفیت)
- راحت‌ترین راه: در PowerShell بزن `winget install Gyan.FFmpeg` و بعد سیستم را ری‌استارت کن.
- یا از [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) دانلود کن و پوشه `bin` را به PATH اضافه کن.
- بدون FFmpeg هم برنامه کار می‌کند، فقط خروجی MP3 غیرفعال است.

---

## 📱 اجرا روی اندروید

### روش ۱: با Termux (پیشنهاد من ⭐)

⚡ **نصب با یک خط:** اینو کپی کن بزن تو ترموکس (از همین گیت‌هاب نصب میشه):
```
pkg update -y && pkg install -y python ffmpeg curl git && cp ~/video-downloader/cookies.txt ~/cookies.bak 2>/dev/null; rm -rf ~/video-downloader && git clone https://github.com/mehradjaan/video-downloader.git ~/video-downloader && cp ~/cookies.bak ~/video-downloader/cookies.txt 2>/dev/null; cd ~/video-downloader && pip install -r requirements.txt && bash setup-termux.sh && vd
```

🔄 **آپدیت برنامه در آینده:**
```
cd ~/video-downloader && git pull
```

روش دستی:

1. اپ **Termux** را از [F-Droid](https://f-droid.org/en/packages/com.termux/) نصب کن (نسخه گوگل‌پلی قدیمی است).
2. این دستورات را یکی‌یکی بزن:
   ```
   pkg update && pkg upgrade
   pkg install python ffmpeg git
   git clone https://github.com/mehradjaan/video-downloader.git ~/video-downloader
   ```
3. برو داخلش و ستاپ کن:
   ```
   cd ~/video-downloader
   pip install -r requirements.txt
   bash setup-termux.sh   # فقط بار اول: ساخت دستور vd و شورتکات
   vd
   ```
   💡 برای دسترسی راحت به حافظه گوشی اول بزن: `termux-setup-storage` و فایل‌ها را در `~/storage/downloads/` کپی کن.
4. مرورگر گوشی (کروم) را باز کن و برو به: **http://localhost:5000**
5. لینک بده و دانلود کن — فایل در پوشه Download مرورگر ذخیره می‌شود. ✅

### ⌨️ اجرای سریع با دستور `vd`
بعد از ستاپ، از این به بعد فقط بنویس:
```
vd
```
اگه کار نکرد، یک بار داخل پوشه برنامه بزن: `bash setup-termux.sh`

### 📲 شورتکات روی صفحه اصلی اندروید
1. اپ **Termux:Widget** را نصب کن (از F-Droid یا گوگل‌پلی — ⚠️ حتماً از همون‌جایی که Termux را گرفتی! اگه Termux از F-Droidـه، Widget هم باید از F-Droid باشه).
2. روی صفحه اصلی گوشی نگه دار → **Widgets** → ویجت **Termux** را اضافه کن.
3. روش بزن و **ویدیو-دانلودر** را انتخاب کن — سرور روشن میشه و مرورگر خودش باز میشه! 🎉

💡 نکته: برای اینکه اندروید سرور را در پس‌زمینه نخوابونه، Battery گوشی برای Termux را روی **Unrestricted** بذار (تنظیمات گوشی → Apps → Termux → Battery). اگه ویجت کار نکرد، تو ترموکس بنویس `vd` تا خطا را ببینی.

### روش ۲: با Pydroid 3
1. اپ **Pydroid 3** را از گوگل‌پلی نصب کن.
2. از منوی PIP این‌ها را نصب کن: `Flask` و `yt-dlp`
3. فایل `app.py` و پوشه `templates` را داخل Pydroid کپی کن و `app.py` را اجرا (دکمه ▶️) کن.
4. آدرس `http://localhost:5000` را در مرورگر گوشی باز کن.

---

## 🍪 دانلود ویدیوهای نیازمند ورود (اینستاگرام خصوصی و...)

ویدیوهای عمومی بدون هیچ کاری دانلود می‌شوند. اگر خطای **Login required** گرفتی:

1. در کامپیوتر با کروم وارد آن سایت شو (مثلاً اینستاگرام).
2. افزونه **Get cookies.txt LOCALLY** را نصب کن و از آن سایت خروجی بگیر.
3. فایل را با اسم دقیق **`cookies.txt`** کنار `app.py` بگذار.
4. برنامه را ری‌استارت کن. ✅

---

## 🔄 آپدیت

سایت‌ها گاهی تغییر می‌کنند؛ راحت‌ترین راه آپدیت موتور دانلود، دکمه **«🔄 آپدیت»** پایین خود برنامه‌ست (بعدش برنامه رو ری‌استارت کن).
یا دستی:
```
pip install -U yt-dlp
```

---

## ❓ رفع اشکال

| مشکل | راه‌حل |
|---|---|
| `pip` شناخته نمی‌شود | پایتون را با تیک Add to PATH دوباره نصب کن |
| خطای FFmpeg برای MP3 | FFmpeg را طبق بالا نصب کن و برنامه را ری‌استارت کن |
| `Unsupported URL` | لینک مستقیم صفحه ویدیو را بده، نه لینک پروفایل/کانال |
| دانلود یوتیوب کند/خطا | VPN را روشن/خاموش کن و دوباره تلاش کن؛ دکمه آپدیت برنامه را بزن |
| صفحه باز نمی‌شود | مطمئن شو برنامه در حال اجراست و آدرس `http://localhost:5000` درست است |
| گوشی: localhost باز نمی‌شود | Termux و مرورگر باید روی همان گوشی باشند |
| دستور `vd` کار نمی‌کند | یک بار داخل پوشه برنامه بزن: `bash setup-termux.sh` |
| ویجت صفحه اصلی کار نمی‌کند | Termux:Widget باید هم‌منبع با Termux باشد (هر دو F-Droid یا هر دو گوگل‌پلی) |

---

## ⚠️ نکته حقوقی

فقط ویدیوهایی را دانلود کن که حقش را داری (ویدیوهای خودت، محتوای آزاد یا با اجازه صاحب اثر). مسئولیت استفاده با خودت است. 🙏

---

👨‍💻 سازنده: **مهراد چناقچی** | 📸 IG: [mehrad_chenaghchi_1990](https://instagram.com/mehrad_chenaghchi_1990)
