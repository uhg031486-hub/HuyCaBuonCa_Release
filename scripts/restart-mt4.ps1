# ============================================
# Script: restart-mt4.ps1
# Mục tiêu: Tắt và bật lại MT4 Exness mỗi 2 tiếng
# ============================================

$AppPath = "C:\Program Files (x86)\exness-mt4-2\terminal.exe"
$ProcessName = "terminal"
$LogFile = "C:\mt4-restart-log.txt"

function Write-Log {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$timestamp] $Message"
    Write-Host $line
    Add-Content -Path $LogFile -Value $line
}

Write-Log "=== Bắt đầu restart MT4 ==="

# Bước 1: Tắt MT4 nếu đang chạy
$process = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue
if ($process) {
    Write-Log "Đang tắt MT4 (PID: $($process.Id))..."
    Stop-Process -Name $ProcessName -Force
    Start-Sleep -Seconds 5
    Write-Log "Đã tắt MT4."
} else {
    Write-Log "MT4 không đang chạy, bỏ qua bước tắt."
}

# Bước 2: Chờ thêm chút cho chắc
Start-Sleep -Seconds 3

# Bước 3: Bật lại MT4
Write-Log "Đang bật lại MT4..."
Start-Process -FilePath $AppPath
Start-Sleep -Seconds 5

# Bước 4: Kiểm tra xem đã bật thành công chưa
$check = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue
if ($check) {
    Write-Log "MT4 đã bật thành công (PID: $($check.Id))."
} else {
    Write-Log "CẢNH BÁO: MT4 không bật được! Kiểm tra lại."
}

Write-Log "=== Restart hoàn tất ==="
