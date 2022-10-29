.\venv\Scripts\pyinstaller.exe ^
    --noconfirm ^
    --noconsole ^
    --onefile ^
    --log-level="WARN" ^
    --add-data="fixedsys.ttf;." ^
    snake.py
