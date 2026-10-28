$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck
$s = New-PSSession -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt

Invoke-Command -Session $s -ScriptBlock {
    Write-Host "=== CONFIG.PY ==="
    Get-Content C:\muse2api\config.py

    Write-Host "`n=== STORE.PY (CƠ CHẾ LẤY TÀI KHOẢN) ==="
    Select-String -Path C:\muse2api\store.py -Pattern 'def pick|def get_account|def next|acquire' -Context 5, 20
}

Remove-PSSession $s
