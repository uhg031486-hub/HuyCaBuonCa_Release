$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck

Invoke-Command -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt -ScriptBlock {
    # 1. Chạy cài đặt Google Drive
    $gdriveInstaller = "C:\Users\Administrator\Downloads\GoogleDriveSetup.exe"
    if (Test-Path $gdriveInstaller) {
        Write-Host "Dang cai dat Google Drive ngam..."
        Start-Process -FilePath $gdriveInstaller -ArgumentList "--silent --desktop_shortcut"
    }

    # 2. Tải và giải nén muse2api
    $zipPath = "C:\Users\Administrator\Downloads\muse2api.zip"
    $targetDir = "C:\muse2api"
    
    Write-Host "Dang tai muse2api tu GitHub..."
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri "https://github.com/czg86389-hub/muse2api/archive/refs/heads/main.zip" -OutFile $zipPath -UseBasicParsing

    if (Test-Path $zipPath) {
        Write-Host "Dang giai nen vao C:\muse2api..."
        $tempDir = "C:\Users\Administrator\Downloads\muse_temp"
        if (Test-Path $tempDir) { Remove-Item -Path $tempDir -Recurse -Force }
        Expand-Archive -Path $zipPath -DestinationPath $tempDir -Force
        
        if (-not (Test-Path $targetDir)) { New-Item -ItemType Directory -Path $targetDir -Force | Out-Null }
        $inner = Get-ChildItem -Path $tempDir -Directory | Select-Object -First 1
        Copy-Item -Path "$($inner.FullName)\*" -Destination $targetDir -Recurse -Force
        Remove-Item -Path $tempDir -Recurse -Force
        Write-Host "Giai nen muse2api hoan tat!"
    }
}
