#!/data/data/com.termux/files/usr/bin/bash
# ⚙️ ستاپ ترموکس برای ویدیو دانلودر
# - می‌سازه: دستور vd (اجرای سریع)
# - می‌سازه: شورتکات ویجت برای صفحه اصلی اندروید
# اجرا (فقط بار اول):  bash setup-termux.sh

APP_DIR="$HOME/video-downloader"

if [ ! -f "$APP_DIR/app.py" ]; then
  echo "❌ فایل app.py پیدا نشد! اول پروژه را در $APP_DIR بریز."
  exit 1
fi

# ─── ۱) دستور vd ───
mkdir -p "$PREFIX/bin"
cat > "$PREFIX/bin/vd" <<'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd "$HOME/video-downloader" || { echo "❌ پوشه video-downloader پیدا نشد!"; exit 1; }
echo "🎬 ویدیو دانلودر در حال اجرا..."
echo "🌐 مرورگر گوشی: http://localhost:5000"
python app.py
EOF
chmod +x "$PREFIX/bin/vd"
echo "✅ دستور vd ساخته شد!"

# ─── ۲) شورتکات ویجت ───
mkdir -p "$HOME/.shortcuts"
cat > "$HOME/.shortcuts/ویدیو-دانلودر.sh" <<'EOF'
#!/data/data/com.termux/files/usr/bin/bash
# ویجت صفحه اصلی: روشن کردن سرور (اگه خاموشه) + باز کردن مرورگر
cd "$HOME/video-downloader" || exit 1
if ! curl -s -o /dev/null -m 2 http://localhost:5000/; then
  nohup python app.py > server.log 2>&1 &
  sleep 4
fi
am start -a android.intent.action.VIEW -d http://localhost:5000 > /dev/null 2>&1 \
  || termux-open-url http://localhost:5000 > /dev/null 2>&1
EOF
chmod +x "$HOME/.shortcuts/ویدیو-دانلودر.sh"
echo "✅ شورتکات ویجت ساخته شد!"
echo ""
echo "📲 برای شورتکات صفحه اصلی: اپ Termux:Widget را نصب کن،"
echo "   بعد ویجت Termux را به صفحه اصلی اضافه کن و «ویدیو-دانلودر» را انتخاب کن."
echo "⌨️ از این به بعد برای اجرا فقط بنویس: vd"
