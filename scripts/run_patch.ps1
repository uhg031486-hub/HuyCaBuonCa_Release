$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck
$s = New-PSSession -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt

Write-Host "1. Copy file patch_rotation.py len VPS..."
Copy-Item -Path "c:\Users\yoga\Documents\Cac Project Cua Huy\AntiGravity\scripts\patch_rotation.py" -Destination "C:\muse2api\patch_rotation.py" -ToSession $s -Force

Write-Host "`n2. Thuc thi patch tren VPS..."
Invoke-Command -Session $s -ScriptBlock {
    C:\muse2api\venv\Scripts\python.exe C:\muse2api\patch_rotation.py
    
    Write-Host "`n3. Khoi dong lai dich vu Muse2API_Service tren VPS..."
    Stop-Process -Name python -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Start-ScheduledTask -TaskName "Muse2API_Service"
    Start-Sleep -Seconds 4
    
    Get-NetTCPConnection -State Listen | Where-Object { $_.LocalPort -eq 18610 } | Select-Object LocalAddress, LocalPort, OwningProcess
}

Remove-PSSession $s
