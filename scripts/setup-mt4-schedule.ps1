# ============================================
# Script: setup-mt4-schedule.ps1
# Chạy script này 1 LẦN để đăng ký lịch tự động
# Chạy với quyền Administrator!
# ============================================

$ScriptPath = "C:\Program Files (x86)\exness-mt4-2\restart-mt4.ps1"
$TaskName = "Restart-MT4-Every-2Hours"

# Xóa task cũ nếu có
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

# Tạo trigger: lặp mỗi 2 tiếng, bắt đầu từ bây giờ, chạy mãi mãi
$trigger = New-ScheduledTaskTrigger `
    -RepetitionInterval (New-TimeSpan -Hours 2) `
    -Once `
    -At (Get-Date)

# Chạy bằng PowerShell với quyền cao nhất
$action = New-ScheduledTaskAction `
    -Execute "PowerShell.exe" `
    -Argument "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$ScriptPath`""

# Chạy dù không có ai đăng nhập (quan trọng cho VPS)
$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 3) `
    -RestartCount 2 `
    -RestartInterval (New-TimeSpan -Minutes 1)

$principal = New-ScheduledTaskPrincipal `
    -UserId "SYSTEM" `
    -LogonType ServiceAccount `
    -RunLevel Highest

Register-ScheduledTask `
    -TaskName $TaskName `
    -Trigger $trigger `
    -Action $action `
    -Settings $settings `
    -Principal $principal `
    -Description "Tự động restart MT4 Exness mỗi 2 tiếng"

Write-Host "✅ Đã đăng ký task '$TaskName' thành công!" -ForegroundColor Green
Write-Host "📋 Kiểm tra tại: Task Scheduler > Task Scheduler Library" -ForegroundColor Cyan
