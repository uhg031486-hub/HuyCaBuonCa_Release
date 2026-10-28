$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck
$s = New-PSSession -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt

Invoke-Command -Session $s -ScriptBlock {
    Select-String -Path C:\muse2api\app.py -Pattern 'HTTP 401' -SimpleMatch
    Select-String -Path C:\muse2api\engine.py -Pattern 'HTTP 401' -SimpleMatch
}

Remove-PSSession $s
