@echo off
setlocal
set ROOT=%~dp0..

echo.
echo  Focus Time Tracking - Demo (4 ports)
echo  ------------------------------------
echo   Version A  API      http://localhost:8100
echo   Version A  Frontend http://localhost:5500
echo   Version B  API      http://localhost:8001
echo   Version B  Frontend http://localhost:5173
echo.

if not exist "%ROOT%\version-A-AI\backend\.venv\Scripts\python.exe" (
  echo [setup] Creating version-A virtualenv...
  pushd "%ROOT%\version-A-AI\backend"
  python -m venv .venv
  call .venv\Scripts\activate
  pip install -r requirements.txt
  popd
)

if not exist "%ROOT%\version-B-Manual\backend\.venv\Scripts\python.exe" (
  echo [setup] Creating version-B virtualenv...
  pushd "%ROOT%\version-B-Manual\backend"
  python -m venv .venv
  call .venv\Scripts\activate
  pip install -r requirements.txt
  popd
)

if not exist "%ROOT%\version-B-Manual\frontend\node_modules" (
  echo [setup] Installing version-B frontend dependencies...
  pushd "%ROOT%\version-B-Manual\frontend"
  call npm install
  popd
)

start "A Backend :8100" cmd /k "cd /d %ROOT%\version-A-AI\backend && call .venv\Scripts\activate && uvicorn main:app --reload --port 8100"
start "A Frontend :5500" cmd /k "cd /d %ROOT%\version-A-AI\frontend && python -m http.server 5500"
start "B Backend :8001" cmd /k "cd /d %ROOT%\version-B-Manual\backend && call .venv\Scripts\activate && uvicorn app.main:app --reload --port 8001"
start "B Frontend :5173" cmd /k "cd /d %ROOT%\version-B-Manual\frontend && npm run dev"

echo All four services started in separate windows.
echo Close those windows (or run scripts\stop-demo.bat) to stop the demo.
