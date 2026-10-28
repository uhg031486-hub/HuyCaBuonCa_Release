$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck

Invoke-Command -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt -ScriptBlock {
    Write-Host "=== 1. TẢI VÀ CÀI ĐẶT GOOGLE DRIVE ==="
    $gdriveInstaller = "C:\Users\Administrator\Downloads\GoogleDriveSetup.exe"
    $gdriveUrl = "https://dl.google.com/drive-file-stream/GoogleDriveSetup.exe"
    
    if (-not (Test-Path "C:\Users\Administrator\Downloads")) {
        New-Item -ItemType Directory -Path "C:\Users\Administrator\Downloads" -Force | Out-Null
    }

    Write-Host "Dang tai GoogleDriveSetup.exe..."
    Invoke-WebRequest -Uri $gdriveUrl -OutFile $gdriveInstaller -UseBasicParsing
    
    if (Test-Path $gdriveInstaller) {
        Write-Host "Dang cai dat Google Drive (silent mode)..."
        $proc = Start-Process -FilePath $gdriveInstaller -ArgumentList "--silent --desktop_shortcut" -Wait -PassThru
        Write-Host "Ket qua cai Google Drive: ExitCode = $($proc.ExitCode)"
    } else {
        Write-Host "Loi: Khong tai duoc GoogleDriveSetup.exe"
    }

    Write-Host "`n=== 2. TẢI VÀ GIẢI NÉN MUSE2API ==="
    $museZip = "C:\Users\Administrator\Downloads\muse2api.zip"
    $museRepoUrl = "https://github.com/czg86389-hub/muse2api/archive/refs/heads/main.zip"
    $museExtractDir = "C:\muse2api"

    Write-Host "Dang tai muse2api tu GitHub..."
    Invoke-WebRequest -Uri $museRepoUrl -OutFile $museZip -UseBasicParsing

    if (Test-Path $museZip) {
        Write-Host "Dang giai nen vao $museExtractDir..."
        if (-not (Test-Path $museExtractDir)) {
            New-Item -ItemType Directory -Path $museExtractDir -Force | Out-Null
        }
        
        $tempExtract = "C:\Users\Administrator\Downloads\muse_temp"
        if (Test-Path $tempExtract) { Remove-Item -Path $tempExtract -Recurse -Force }
        Expand-Archive -Path $museZip -DestinationPath $tempExtract -Force
        
        # Copy các file từ folder con muse2api-main ra thẳng C:\muse2api
        $subFolder = Get-ChildItem -Path $tempExtract -Directory | Select-Object -First 1
        if ($subFolder) {
            Copy-Item -Path "$($subFolder.FullName)\*" -Destination $museExtractDir -Recurse -Force
            Write-Host "Da giai nen code muse2api thanh cong vao $museExtractDir!"
        }
        Remove-Item -Path $tempExtract -Recurse -Force
    }

    Write-Host "`n=== 3. KIỂM TRA THƯ MỤC C:\muse2api ==="
    Get-ChildItem -Path $museExtractDir | Select-Object Name, Length
}
