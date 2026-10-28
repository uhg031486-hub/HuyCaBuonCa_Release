$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck

Invoke-Command -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt -ScriptBlock {
    # 1. Tạo file run_muse2api.vbs để chạy ngầm không hiện cửa sổ
    $vbsContent = @"
Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\muse2api"
WshShell.Run "C:\muse2api\venv\Scripts\python.exe -m uvicorn app:app --host 0.0.0.0 --port 18610", 0, False
"@
    Set-Content -Path "C:\muse2api\run_hidden.vbs" -Value $vbsContent -Encoding ASCII
    Write-Host "Da tao C:\muse2api\run_hidden.vbs"

    # 2. Tạo file bat start_muse2api.bat
    $batContent = @"
@echo off
cd /d C:\muse2api
C:\muse2api\venv\Scripts\python.exe -m uvicorn app:app --host 0.0.0.0 --port 18610
"@
    Set-Content -Path "C:\muse2api\start.bat" -Value $batContent -Encoding ASCII

    # 3. Mở cổng Firewall 18610 cho muse2api
    New-NetFirewallRule -DisplayName "MUSE2API Port 18610" -Direction Inbound -LocalPort 18610 -Protocol TCP -Action Allow -ErrorAction SilentlyContinue | Out-Null
    Write-Host "Da mo cong Firewall 18610 tren VPS"

    # 4. Khởi chạy muse2api ngay lập tức qua vbs
    wscript.exe "C:\muse2api\run_hidden.vbs"
    Start-Sleep -Seconds 5

    # 5. Kiểm tra tiến trình đang chạy và test port
    Get-Process -Name python -ErrorAction SilentlyContinue | Select-Object Id, ProcessName
    Test-NetConnection -ComputerName 127.0.0.1 -Port 18610 | Select-Object TcpTestSucceeded
}
