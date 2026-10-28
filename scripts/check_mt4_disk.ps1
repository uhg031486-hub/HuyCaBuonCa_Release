$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck

Invoke-Command -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt -ScriptBlock {
    # 1. Thư mục cài đặt MT4 ở C:\
    $folders = Get-ChildItem -Path C:\ -Directory | Where-Object { $_.Name -like '*MetaTrader*' -or $_.Name -like '*exness*' }
    
    # 2. Thư mục dữ liệu AppData của MT4 (nơi chứa history, logs, tester data)
    $appData = "C:\Users\Administrator\AppData\Roaming\MetaQuotes"
    $appDataUsers = Get-ChildItem -Path C:\Users -Directory | ForEach-Object {
        $mq = Join-Path $_.FullName "AppData\Roaming\MetaQuotes"
        if (Test-Path $mq) { Get-Item $mq }
    }

    $allToCheck = @($folders) + @($appDataUsers)

    $report = foreach ($f in $allToCheck) {
        $files = Get-ChildItem -LiteralPath $f.FullName -Recurse -File -Force -ErrorAction SilentlyContinue
        $totalBytes = ($files | Measure-Object -Property Length -Sum).Sum
        [PSCustomObject]@{
            Folder = $f.FullName
            Files = $files.Count
            Size_MB = [math]::Round(($totalBytes / 1MB), 2)
            Size_GB = [math]::Round(($totalBytes / 1GB), 2)
        }
    }

    $report | Format-Table -AutoSize
}
