@echo off
echo ============================================
echo   LaunchPad - بناء ملف التطبيق
echo ============================================
echo.

:: Install dependencies
echo [1/3] تثبيت المتطلبات...
pip install -r requirements.txt
if errorlevel 1 goto error

:: Build EXE
echo [2/3] بناء ملف التطبيق...
pyinstaller ^
  --onefile ^
  --windowed ^
  --name "LaunchPad" ^
  --icon "icon.ico" ^
  --add-data "." ^
  --clean ^
  main.py

if errorlevel 1 goto error

echo [3/3] تم بنجاح!
echo.
echo الملف موجود في: dist\LaunchPad.exe
echo.
pause
goto end

:error
echo.
echo حدث خطأ أثناء البناء!
pause

:end
