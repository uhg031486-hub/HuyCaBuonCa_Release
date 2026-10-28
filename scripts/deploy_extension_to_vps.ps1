$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck
$s = New-PSSession -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt

Write-Host "1. Tim kiem cac thu muc extension tren VPS..."
$found = Invoke-Command -Session $s -ScriptBlock {
    Get-ChildItem -Path C:\ -Filter "manifest.json" -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.DirectoryName -like "*extension*" -or $_.DirectoryName -like "*muse*" } | Select-Object -ExpandProperty DirectoryName
}

Write-Host "Cac thu muc extension tim thay tren VPS:"
$found

Write-Host "`n2. Sao chep bo extension Tieng Viet len VPS..."
# Thu muc chinh C:\muse2api\extension
Copy-Item -Path "C:\Users\yoga\Downloads\muse2api-extension (1)\muse2api-extension\*" -Destination "C:\muse2api\extension\" -ToSession $s -Recurse -Force
Write-Host "Da copy vao C:\muse2api\extension"

# Neu nguoi dung co giai nen o Downloads tren VPS, copy them vao do
foreach ($dir in $found) {
    if ($dir -ne "C:\muse2api\extension") {
        Write-Host "Dang cap nhat vao: $dir"
        Copy-Item -Path "C:\Users\yoga\Downloads\muse2api-extension (1)\muse2api-extension\*" -Destination "$dir\" -ToSession $s -Recurse -Force
    }
}

Write-Host "`nHoan tat cap nhat extension Tieng Viet tren VPS!"
Remove-PSSession $s
