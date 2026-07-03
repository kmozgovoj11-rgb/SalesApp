$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $Root

$Runtime = Join-Path $Root "runtime\python"
$PyVer = "3.12.10"
$PyZip = "python-$PyVer-embed-amd64.zip"
$PyUrl = "https://www.python.org/ftp/python/$PyVer/$PyZip"
$GetPipUrl = "https://bootstrap.pypa.io/get-pip.py"

Write-Host "============================================"
Write-Host "  SalesApp portable build"
Write-Host "============================================"
Write-Host ""

if (-not (Test-Path (Join-Path $Root "salesapp\ui.py"))) {
    throw "salesapp\ui.py not found. Run from project root."
}

if (-not (Test-Path (Join-Path $Runtime "python.exe"))) {
    Write-Host "[1/4] Downloading Python $PyVer ..."
    $runtimeDir = Join-Path $Root "runtime"
    if (-not (Test-Path $runtimeDir)) {
        New-Item -ItemType Directory -Path $runtimeDir | Out-Null
    }

    $tempZip = Join-Path $env:TEMP $PyZip
    Invoke-WebRequest -Uri $PyUrl -OutFile $tempZip

    Write-Host "[2/4] Extracting Python ..."
    if (Test-Path $Runtime) {
        Remove-Item $Runtime -Recurse -Force
    }
    Expand-Archive -LiteralPath $tempZip -DestinationPath $Runtime -Force
} else {
    Write-Host "[1/4] Python already exists."
    Write-Host "[2/4] Python already extracted."
}

Write-Host "[3/4] Setting up pip ..."
$pth = Get-ChildItem -Path $Runtime -Filter "python*._pth" | Select-Object -First 1
if (-not $pth) {
    throw "python*._pth not found"
}
Set-Content -Path $pth.FullName -Value @(
    "python312.zip",
    ".",
    "Lib\site-packages",
    "import site"
) -Encoding Ascii

$getPip = Join-Path $env:TEMP "get-pip.py"
Invoke-WebRequest -Uri $GetPipUrl -OutFile $getPip
& (Join-Path $Runtime "python.exe") $getPip --no-warn-script-location

Write-Host "[4/4] Installing dependencies ..."
& (Join-Path $Runtime "python.exe") -m pip install --upgrade pip --no-warn-script-location
& (Join-Path $Runtime "python.exe") -m pip install -r (Join-Path $Root "requirements.txt") --no-warn-script-location

Write-Host ""
Write-Host "Creating ZIP archive ..."
$ZipPath = Join-Path ([Environment]::GetFolderPath("Desktop")) "sales_app_client.zip"
if (Test-Path $ZipPath) {
    Remove-Item $ZipPath -Force
}

$pathsToZip = @(
    "salesapp",
    "data",
    "assets",
    "scripts",
    "docs",
    ".streamlit",
    "start.bat",
    "create_shortcut.bat",
    "build_client.bat",
    "requirements.txt",
    "runtime"
)

$staging = Join-Path $env:TEMP "sales_app_client_staging"
if (Test-Path $staging) {
    Remove-Item $staging -Recurse -Force
}
New-Item -ItemType Directory -Path $staging | Out-Null

foreach ($item in $pathsToZip) {
    $source = Join-Path $Root $item
    if (Test-Path $source) {
        Copy-Item -Path $source -Destination $staging -Recurse -Force
    }
}

Compress-Archive -Path (Join-Path $staging "*") -DestinationPath $ZipPath -Force
Remove-Item $staging -Recurse -Force

Write-Host ""
Write-Host "Done: $ZipPath"
Write-Host "Client: unzip -> create_shortcut.bat -> SalesApp icon"
