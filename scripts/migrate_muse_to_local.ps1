$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck
$s = New-PSSession -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt

Write-Host "1. Tat dich vu Muse2API_Service va kill sach chrome tren VPS de giai phong VPS..."
Invoke-Command -Session $s -ScriptBlock {
    Stop-ScheduledTask -TaskName "Muse2API_Service" -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName "Muse2API_Service" -Confirm:$false -ErrorAction SilentlyContinue
    Stop-Process -Name python -Force -ErrorAction SilentlyContinue
    Stop-Process -Name chrome -Force -ErrorAction SilentlyContinue
    Write-Host "-> VPS da duoc giai phong hoan toan RAM va tat dich vu Muse2API!"
}

Write-Host "`n2. Tao thu muc C:\muse2api tren may laptop..."
if (-not (Test-Path "C:\muse2api")) {
    New-Item -ItemType Directory -Path "C:\muse2api" -Force | Out-Null
}

Write-Host "`n3. Sao chep toan bo code va data tu VPS ve may laptop..."
Copy-Item -FromSession $s -Path "C:\muse2api\*" -Destination "C:\muse2api\" -Recurse -Force -Exclude "venv", "__pycache__"

Remove-PSSession $s
Write-Host "-> Sao chep thanh cong ve C:\muse2api tren may laptop!"
