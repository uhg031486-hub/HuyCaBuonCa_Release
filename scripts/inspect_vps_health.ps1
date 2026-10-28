$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck
$s = New-PSSession -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt

Invoke-Command -Session $s -ScriptBlock {
    Write-Host "=== TAI NGUYEN HE THONG ==="
    $os = Get-CimInstance Win32_OperatingSystem
    $totalRam = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
    $freeRam = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
    $usedRam = [math]::Round($totalRam - $freeRam, 2)
    $ramPct = [math]::Round(($usedRam / $totalRam) * 100, 1)
    $cpu = (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average
    Write-Host "CPU: $cpu % | RAM: $usedRam GB / $totalRam GB ($ramPct %)"

    Write-Host "`n=== TIEN TRINH CHROME ==="
    $chromes = Get-Process -Name chrome -ErrorAction SilentlyContinue
    Write-Host "So luong chrome: $($chromes.Count)"

    Write-Host "`n=== TOP 5 TIEN TRINH NGON CPU & RAM ==="
    Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 5 ProcessName, Id, @{Name="RAM(MB)"; Expression={[math]::Round($_.WorkingSet64/1MB,1)}}, CPU | Format-Table -AutoSize

    Write-Host "`n=== TIEN TRINH PYTHON UVICORN ==="
    Get-Process -Name python -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, WorkingSet64, CPU

    Write-Host "`n=== DICH VU 9ROUTER ==="
    Get-Process -Id (Get-NetTCPConnection -State Listen | Where-Object { $_.LocalPort -eq 20128 }).OwningProcess -ErrorAction SilentlyContinue
}

Remove-PSSession $s
