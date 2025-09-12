@echo off
chcp 65001 >nul
cd /d "%~dp0"
where poetry >nul 2>&1 || (
  echo 找不到 poetry，請確認已安裝並加入 PATH。
  pause
  exit /b 1
)
poetry run streamlit run home.py
echo Streamlit 已結束。
pause
