@echo off
cd /d "%~dp0"
echo ==== %date% %time% >> .private\sync.log
"C:\Users\tukum\AppData\Local\Programs\Python\Python314\python.exe" sync.py --push >> .private\sync.log 2>&1
