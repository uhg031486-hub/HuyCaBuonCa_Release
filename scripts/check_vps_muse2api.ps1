$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck
$session = New-PSSession -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt

Invoke-Command -Session $session -ScriptBlock {
    Write-Host "=== KIEM TRA PORT DANG LISTEN ==="
    Get-NetTCPConnection -State Listen | Where-Object { $_.LocalPort -in @(18610, 20128, 19210) } | Select-Object LocalAddress, LocalPort, OwningProcess

    Write-Host "`n=== KIEM TRA PROCESS PYTHON & CHROME ==="
    Get-Process -Name python, chrome -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, CPU, WorkingSet

    Write-Host "`n=== KIEM TRA SCHEDULED TASKS ==="
    Get-ScheduledTask -TaskName "Muse2API_AutoStart" -ErrorAction SilentlyContinue | Select-Object TaskName, State
}

Remove-PSSession $session
