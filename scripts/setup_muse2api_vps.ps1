$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck
$session = New-PSSession -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt

Write-Host "Dang copy code muse2api len VPS tai C:\muse2api..."
Copy-Item -Path "C:\Users\yoga\Downloads\muse_local\muse2api-main\*" -Destination "C:\muse2api" -ToSession $session -Recurse -Force

Write-Host "Copy thanh cong! Dang tao file .env va cai dat thu vien Python tren VPS..."
Invoke-Command -Session $session -ScriptBlock {
    # 1. Tạo file .env
    $envContent = @"
MUSE2API_KEY=m2a_quanghuy_2026_secret
MUSE2API_HOST=0.0.0.0
MUSE2API_PORT=18610
MUSE2API_PUBLIC_BASE=
MUSE2API_CHROMIUM=C:\Program Files\Google\Chrome\Application\chrome.exe
MUSE2API_CDP_PORT=19210
MUSE2API_IMAGE_TIMEOUT=240
MUSE2API_VIDEO_TIMEOUT=600
MUSE2API_CHAT_TIMEOUT=300
MUSE2API_CONCURRENCY=2
MUSE2API_KEEPALIVE_DISABLED_ACCOUNTS=0
"@
    Set-Content -Path "C:\muse2api\.env" -Value $envContent -Encoding UTF8
    Write-Host "Da tao file C:\muse2api\.env"

    # 2. Tạo virtualenv Python và cài đặt requirements
    Set-Location "C:\muse2api"
    if (-not (Test-Path "C:\muse2api\venv")) {
        Write-Host "Dang tao moi truong Python venv..."
        python -m venv venv
    }

    Write-Host "Dang cai dat cac thu vien Python (FastAPI, uvicorn, requests, websocket...)..."
    .\venv\Scripts\python.exe -m pip install --upgrade pip
    .\venv\Scripts\python.exe -m pip install -r requirements.txt
    Write-Host "Cai dat pip requirements hoan tat!"
}

Remove-PSSession $session
