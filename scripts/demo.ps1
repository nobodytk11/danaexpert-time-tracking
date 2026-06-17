$Root = Split-Path $PSScriptRoot -Parent

Write-Host ""
Write-Host " Focus Time Tracking - Demo (4 ports)"
Write-Host " ------------------------------------"
Write-Host "  Version A  API      http://localhost:8100"
Write-Host "  Version A  Frontend http://localhost:5500"
Write-Host "  Version B  API      http://localhost:8001"
Write-Host "  Version B  Frontend http://localhost:5173"
Write-Host ""

function Ensure-Venv($BackendDir) {
    $py = Join-Path $BackendDir ".venv\Scripts\python.exe"
    if (-not (Test-Path $py)) {
        Write-Host "[setup] Creating virtualenv in $BackendDir"
        Push-Location $BackendDir
        python -m venv .venv
        & .\.venv\Scripts\pip.exe install -r requirements.txt
        Pop-Location
    }
    return $py
}

$A_py = Ensure-Venv (Join-Path $Root "version-A-AI\backend")
$B_py = Ensure-Venv (Join-Path $Root "version-B-Manual\backend")

$feB = Join-Path $Root "version-B-Manual\frontend"
if (-not (Test-Path (Join-Path $feB "node_modules"))) {
    Write-Host "[setup] npm install in version-B frontend"
    Push-Location $feB
    npm install
    Pop-Location
}

Start-Process cmd -ArgumentList "/k", "cd /d `"$(Join-Path $Root 'version-A-AI\backend')`" && .venv\Scripts\activate && uvicorn main:app --reload --port 8100" -WindowStyle Normal
Start-Process cmd -ArgumentList "/k", "cd /d `"$(Join-Path $Root 'version-A-AI\frontend')`" && python -m http.server 5500" -WindowStyle Normal
Start-Process cmd -ArgumentList "/k", "cd /d `"$(Join-Path $Root 'version-B-Manual\backend')`" && .venv\Scripts\activate && uvicorn app.main:app --reload --port 8001" -WindowStyle Normal
Start-Process cmd -ArgumentList "/k", "cd /d `"$feB`" && npm run dev" -WindowStyle Normal

Write-Host "All four services started in separate windows."
