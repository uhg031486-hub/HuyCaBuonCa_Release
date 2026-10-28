$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck
$s = New-PSSession -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt

Invoke-Command -Session $s -ScriptBlock {
    Stop-Process -Name python -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Start-ScheduledTask -TaskName "Muse2API_Service"
    Start-Sleep -Seconds 4
    Get-NetTCPConnection -State Listen | Where-Object { $_.LocalPort -in @(18610, 19210) } | Select-Object LocalPort, OwningProcess
}

Remove-PSSession $s
