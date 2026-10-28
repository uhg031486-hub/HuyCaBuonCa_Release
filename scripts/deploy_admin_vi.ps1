$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck
$session = New-PSSession -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt

Write-Host "Dang sao chep file admin_vi.html len C:\muse2api\admin.html tren VPS..."
Copy-Item -Path "c:\Users\yoga\Documents\Cac Project Cua Huy\AntiGravity\scripts\admin_vi.html" -Destination "C:\muse2api\admin.html" -ToSession $session -Force

Write-Host "Sao chep thanh cong! admin.html tren VPS da duoc Viet hoa 100%."
Remove-PSSession $session
