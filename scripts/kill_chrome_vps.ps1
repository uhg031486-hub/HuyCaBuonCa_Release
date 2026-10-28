$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck

$ips = @('100.92.145.57', '222.255.184.149')

foreach ($ip in $ips) {
    Write-Host "Dang thu ket noi toi $ip..."
    try {
        $s = New-PSSession -ComputerName $ip -Credential $cred -UseSSL -SessionOption $opt -ErrorAction Stop
        Write-Host "-> KET NOI THANH CONG TOI $ip !"
        Invoke-Command -Session $s -ScriptBlock {
            Write-Host "=== DANG DÒN DẸP TIẾN TRÌNH TRÊN VPS ==="
            $before = (Get-Process -Name chrome -ErrorAction SilentlyContinue).Count
            Write-Host "So luong process Chrome truoc khi don: $before"
            Stop-Process -Name chrome -Force -ErrorAction SilentlyContinue
            Write-Host "Da tat toan bo tien trinh Chrome!"

            Write-Host "`n=== KHOI DONG LAI MUSE2API NHẸ NHÀNG ==="
            Start-ScheduledTask -TaskName "Muse2API_Service"
            Start-Sleep -Seconds 3

            $os = Get-CimInstance Win32_OperatingSystem
            $freeRam = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
            $totalRam = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
            Write-Host "RAM trong hien tai: $freeRam GB / $totalRam GB"
        }
        Remove-PSSession $s
        Write-Host "HOAN TAT DON DEP!"
        exit 0
    } catch {
        Write-Host "-> Loi ket noi toi $ip : $_"
    }
}
