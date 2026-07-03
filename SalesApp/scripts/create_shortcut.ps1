$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$IconPng = Join-Path $Root "assets\app_icon.png"
$IconIco = Join-Path $Root "assets\app_icon.ico"
$StartBat = Join-Path $Root "start.bat"
$ShortcutName = "SalesApp.lnk"
$DesktopShortcut = Join-Path ([Environment]::GetFolderPath("Desktop")) $ShortcutName
$LocalShortcut = Join-Path $Root $ShortcutName

if (-not (Test-Path $StartBat)) {
    throw "start.bat not found"
}

if (-not (Test-Path $IconPng)) {
    throw "assets/app_icon.png not found"
}

$PythonExe = Join-Path $Root "runtime\python\python.exe"
if (Test-Path $PythonExe) {
    & $PythonExe (Join-Path $PSScriptRoot "make_icon.py")
} else {
    Add-Type -AssemblyName System.Drawing
    $bitmap = New-Object System.Drawing.Bitmap($IconPng)
    $iconHandle = $bitmap.GetHicon()
    $icon = [System.Drawing.Icon]::FromHandle($iconHandle)
    $fileStream = New-Object System.IO.FileStream($IconIco, [System.IO.FileMode]::Create)
    $icon.Save($fileStream)
    $fileStream.Close()
    $icon.Dispose()
    $bitmap.Dispose()
}

if (-not (Test-Path $IconIco)) {
    throw "assets/app_icon.ico was not created"
}

$shell = New-Object -ComObject WScript.Shell

$desktopLink = $shell.CreateShortcut($DesktopShortcut)
$desktopLink.TargetPath = $StartBat
$desktopLink.WorkingDirectory = $Root
$desktopLink.WindowStyle = 1
$desktopLink.IconLocation = "$IconIco,0"
$desktopLink.Save()

$localLink = $shell.CreateShortcut($LocalShortcut)
$localLink.TargetPath = $StartBat
$localLink.WorkingDirectory = $Root
$localLink.WindowStyle = 1
$localLink.IconLocation = "$IconIco,0"
$localLink.Save()

Write-Host "Shortcut updated: $DesktopShortcut"
