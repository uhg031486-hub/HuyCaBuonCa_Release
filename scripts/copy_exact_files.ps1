$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck
$s = New-PSSession -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt

$files = @(
    "app.py",
    "cdp.py",
    "config.py",
    "engine.py",
    "store.py",
    "requirements.txt",
    "admin.html",
    ".env",
    "data\accounts.json"
)

foreach ($f in $files) {
    Write-Host "Copying $f..."
    Copy-Item -FromSession $s -Path "C:\muse2api\$f" -Destination "C:\muse2api\$f" -Force
}

Remove-PSSession $s
Write-Host "HOAN TAT COPY CODE VA DATA VE LOCAL!"
