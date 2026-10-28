$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck
$s = New-PSSession -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt

Invoke-Command -Session $s -ScriptBlock {
    Write-Host "=== KIEM TRA HATCH_GW TRONG SOURCE CODE ==="
    Select-String -Path C:\muse2api\*.py -Pattern 'hatch_gw'
    Write-Host "`n=== KIEM TRA ESSENTIAL TRONG STORE HOAC APP ==="
    Select-String -Path C:\muse2api\*.py -Pattern 'ESSENTIAL'
}

Remove-PSSession $s
