$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck
$s = New-PSSession -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt

Invoke-Command -Session $s -ScriptBlock {
    Write-Host "=== KIEM TRA TRANG THAI CHROME CDP ==="
    try {
        $cdp = Invoke-RestMethod -Uri "http://127.0.0.1:19210/json/version" -TimeoutSec 3
        $cdp | ConvertTo-Json
    } catch {
        Write-Host "Loi ket noi CDP port 19210: $_"
    }

    Write-Host "`n=== KIEM TRA CAC TAB DANG MO TRONG CDP ==="
    try {
        $tabs = Invoke-RestMethod -Uri "http://127.0.0.1:19210/json/list" -TimeoutSec 3
        $tabs | Select-Object id, title, url | Format-Table -AutoSize
    } catch {
        Write-Host "Loi lay danh sach tab CDP: $_"
    }
}

Remove-PSSession $s
