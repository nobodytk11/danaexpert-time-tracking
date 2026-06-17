@echo off
echo Stopping demo services on ports 8100, 5500, 8001, 5173...

for %%P in (8100 5500 8001 5173) do (
  for /f "tokens=5" %%A in ('netstat -ano ^| findstr /R /C:":%%P .*LISTENING"') do (
    echo Killing PID %%A on port %%P
    taskkill /F /PID %%A >nul 2>&1
  )
)

echo Done.
