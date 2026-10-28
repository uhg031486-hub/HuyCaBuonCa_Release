$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck
$s = New-PSSession -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt

Invoke-Command -Session $s -ScriptBlock {
    Write-Host "=== PORT 18610 BINDING ==="
    Get-NetTCPConnection -State Listen | Where-Object { $_.LocalPort -eq 18610 } | Format-Table LocalAddress, LocalPort, OwningProcess -AutoSize

    Write-Host "`n=== FIREWALL RULES 18610 ==="
    Get-NetFirewallRule -DisplayName '*18610*' | Format-Table DisplayName, Enabled, Direction, Action, Profile -AutoSize

    Write-Host "`n=== TAO LAI RULE MO TOAN BO PROFILE ==="
    Remove-NetFirewallRule -DisplayName '*18610*' -ErrorAction SilentlyContinue
    New-NetFirewallRule -DisplayName "MUSE2API Port 18610" -Direction Inbound -LocalPort 18610 -Protocol TCP -Action Allow -Profile Any
}

Remove-PSSession $s
