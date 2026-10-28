$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck
$s = New-PSSession -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt

Invoke-Command -Session $s -ScriptBlock {
    # 1. Tạo file bat khởi chạy chuẩn
    $batPath = "C:\muse2api\run_service.bat"
    $batContent = @"
@echo off
cd /d C:\muse2api
C:\muse2api\venv\Scripts\python.exe -m uvicorn app:app --host 0.0.0.0 --port 18610
"@
    Set-Content -Path $batPath -Value $batContent -Encoding ASCII

    # 2. Xóa task cũ nếu có
    Unregister-ScheduledTask -TaskName "Muse2API_Service" -Confirm:$false -ErrorAction SilentlyContinue

    # 3. Tạo Scheduled Task chạy dưới SYSTEM, không bao giờ dừng, tự start lại
    $action = New-ScheduledTaskAction -Execute $batPath -WorkingDirectory "C:\muse2api"
    $trigger = New-ScheduledTaskTrigger -AtStartup
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit (New-TimeSpan -Days 999)
    $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

    Register-ScheduledTask -TaskName "Muse2API_Service" -Action $action -Trigger $trigger -Settings $settings -Principal $principal
    Start-ScheduledTask -TaskName "Muse2API_Service"

    Start-Sleep -Seconds 5
    Get-ScheduledTask -TaskName "Muse2API_Service" | Select-Object TaskName, State
    Get-NetTCPConnection -State Listen | Where-Object { $_.LocalPort -eq 18610 } | Select-Object LocalAddress, LocalPort, OwningProcess
}

Remove-PSSession $s
