$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck
$s = New-PSSession -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt

Write-Host "1. Quet thu muc extension tren VPS..."
$dirsToCheck = @(
    "C:\muse2api\extension",
    "C:\Users\Administrator\Downloads",
    "C:\Users\Administrator\Desktop"
)

$targetDirs = Invoke-Command -Session $s -ArgumentList (,$dirsToCheck) -ScriptBlock {
    param($dirs)
    $list = @()
    foreach ($d in $dirs) {
        if (Test-Path $d) {
            $manifests = Get-ChildItem -Path $d -Filter "manifest.json" -Recurse -ErrorAction SilentlyContinue
            foreach ($m in $manifests) {
                $list += $m.DirectoryName
            }
        }
    }
    return $list | Select-Object -Unique
}

Write-Host "Cac thu muc chua Extension tren VPS:"
$targetDirs

Write-Host "`n2. Sao chep ban Tieng Viet vao tat ca cac thu muc tren..."
# Luon dam bao C:\muse2api\extension co
if (-not (Invoke-Command -Session $s -ScriptBlock { Test-Path "C:\muse2api\extension" })) {
    Invoke-Command -Session $s -ScriptBlock { New-Item -ItemType Directory -Path "C:\muse2api\extension" -Force }
}

Copy-Item -Path "C:\Users\yoga\Downloads\muse2api-extension (1)\muse2api-extension\*" -Destination "C:\muse2api\extension\" -ToSession $s -Recurse -Force
Write-Host "-> Da chep vao C:\muse2api\extension"

foreach ($dir in $targetDirs) {
    if ($dir -ne "C:\muse2api\extension") {
        Write-Host "-> Dang chep vao $dir"
        Copy-Item -Path "C:\Users\yoga\Downloads\muse2api-extension (1)\muse2api-extension\*" -Destination "$dir\" -ToSession $s -Recurse -Force
    }
}

Write-Host "`nHoan tat cap nhat extension Tieng Viet tren VPS!"
Remove-PSSession $s
