@echo off
echo 🤖 Öğrenen Asistan Başlatılıyor...
echo.

REM Sanal ortamı kontrol et
if not exist ".venv" (
    echo ⚠️ Sanal ortam bulunamadı! Kurulum gerekli.
    echo Lütfen README.md dosyasındaki kurulum talimatlarını takip edin.
    pause
    exit /b 1
)

REM Gerekli paketleri kontrol et
echo 📦 Gerekli paketler kontrol ediliyor...
.venv\Scripts\python.exe -c "import colorama, fuzzywuzzy" 2>nul
if errorlevel 1 (
    echo ⚠️ Gerekli paketler bulunamadı! Yükleniyor...
    .venv\Scripts\pip.exe install -r requirements.txt
)

REM Asistanı başlat
echo.
echo ✅ Öğrenen Asistan başlatılıyor...
echo.
.venv\Scripts\python.exe asistan.py

pause
