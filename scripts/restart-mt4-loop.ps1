# ============================================
# Script: restart-mt4-loop.ps1
# Phiên bản chuẩn: Chỉ tắt và bật đúng Exness MT4 2 NGAY LẬP TỨC!
# Không động vào các MT4 khác (MT4 1, MT4 3...)
# ============================================

$AppPath       = "C:\Program Files (x86)\exness-mt4-2\terminal.exe"
$TargetFolder  = "exness-mt4-2"
$LogFile       = "$env:USERPROFILE\mt4-restart-log.txt"
$IntervalHours = 2   # Chu kỳ restart: 2 tiếng

function Write-Log {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$timestamp] $Message"
    Write-Host $line
    Add-Content -Path $LogFile -Value $line
}

Write-Log "====== MT4 2 Auto-Restart bắt đầu chạy ======"
Write-Log "Mục tiêu: CHỈ restart MT4 trong thư mục $TargetFolder (mở lại ngay lập tức)"
Write-Log "Chu kỳ restart: mỗi $IntervalHours tiếng"
Write-Host ""
Write-Host "Để dừng script: nhấn Ctrl+C hoặc đóng cửa sổ này." -ForegroundColor Yellow
Write-Host ""

while ($true) {
    $nextRestart = (Get-Date).AddHours($IntervalHours)
    Write-Log "Lần restart tiếp theo: $($nextRestart.ToString('HH:mm:ss dd/MM/yyyy'))"

    # Đợi đủ 2 tiếng
    Start-Sleep -Seconds ($IntervalHours * 3600)

    Write-Log "--- Bắt đầu restart Exness MT4 2 ---"

    # Lọc CHÍNH XÁC process terminal.exe chạy từ thư mục exness-mt4-2
    $processes = Get-CimInstance Win32_Process -Filter "Name = 'terminal.exe'" | Where-Object {
        $_.ExecutablePath -like "*$TargetFolder*"
    }

    if ($processes) {
        foreach ($proc in $processes) {
            Write-Log "Đang tắt Exness MT4 2 (PID: $($proc.ProcessId))..."
            Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue
        }
        Write-Log "Đã tắt Exness MT4 2."
    } else {
        Write-Log "Exness MT4 2 không đang chạy, tiến hành bật mới."
    }

    # Chờ 1 giây siêu ngắn để Windows nhả file lock
    Start-Sleep -Seconds 1

    # Bật lại NGAY LẬP TỨC
    Write-Log "Đang bật lại Exness MT4 2 ngay lập tức..."
    Start-Process -FilePath $AppPath -WorkingDirectory "C:\Program Files (x86)\exness-mt4-2"

    Start-Sleep -Seconds 2

    # Kiểm tra lại xem process của MT4 2 đã lên chưa
    $check = Get-CimInstance Win32_Process -Filter "Name = 'terminal.exe'" | Where-Object {
        $_.ExecutablePath -like "*$TargetFolder*"
    }
    if ($check) {
        Write-Log "✅ Exness MT4 2 đã bật lại thành công (PID: $($check.ProcessId))."
    } else {
        Write-Log "⚠️ CẢNH BÁO: Exness MT4 2 không bật được!"
    }

    Write-Log "--- Restart MT4 2 hoàn tất ---"
    Write-Host ""
}
