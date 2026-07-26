$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

function Refresh-Path {
    $machinePath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path = "$machinePath;$userPath"
}

function Find-Python312 {
    $candidates = @()

    # Prefer an explicitly installed CPython 3.12 interpreter.
    $known = @(
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:ProgramFiles\Python312\python.exe",
        "${env:ProgramFiles(x86)}\Python312\python.exe"
    )
    foreach ($path in $known) {
        if ($path -and (Test-Path $path)) { $candidates += $path }
    }

    # Python Launcher may already know where 3.12 is installed.
    $py = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($py) {
        try {
            $path = (& $py.Source -3.12 -c "import sys; print(sys.executable)" 2>$null | Select-Object -First 1)
            if ($LASTEXITCODE -eq 0 -and $path -and (Test-Path $path)) { $candidates += $path.Trim() }
        } catch {}
    }

    # Fall back to python.exe only when it is exactly Python 3.12.
    foreach ($name in @("python.exe", "python3.exe")) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd) {
            try {
                $minor = (& $cmd.Source -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null | Select-Object -First 1)
                if ($LASTEXITCODE -eq 0 -and $minor.Trim() -eq "3.12") { $candidates += $cmd.Source }
            } catch {}
        }
    }

    return ($candidates | Select-Object -Unique | Select-Object -First 1)
}

function Ensure-Winget {
    $winget = Get-Command winget.exe -ErrorAction SilentlyContinue
    if (-not $winget) {
        throw "Windows Package Manager (winget) is not available. Install/update 'App Installer' from Microsoft Store, then run this file again."
    }
    return $winget.Source
}

Write-Host "[1/5] Checking Python 3.12..." -ForegroundColor Cyan
$python = Find-Python312
if (-not $python) {
    Write-Host "Python 3.12 was not found. Installing it automatically..." -ForegroundColor Yellow
    $winget = Ensure-Winget
    & $winget install --id Python.Python.3.12 -e --scope user --silent --accept-package-agreements --accept-source-agreements --disable-interactivity
    if ($LASTEXITCODE -ne 0) {
        throw "Automatic Python 3.12 installation failed (winget exit code $LASTEXITCODE)."
    }
    Refresh-Path
    Start-Sleep -Seconds 2
    $python = Find-Python312
    if (-not $python) {
        throw "Python 3.12 was installed but could not be located. Close this window and run build_installer.bat once more."
    }
}
Write-Host "Using: $python" -ForegroundColor DarkGray

Write-Host "[2/5] Installing Python build dependencies..." -ForegroundColor Cyan
& $python -m ensurepip --upgrade 2>$null
& $python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed." }
& $python -m pip install -r requirements.txt pyinstaller==6.10.0
if ($LASTEXITCODE -ne 0) { throw "Python dependency installation failed." }

Write-Host "[3/5] Building LockIt.exe..." -ForegroundColor Cyan
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
& $python -m PyInstaller --noconfirm --clean LockIt.spec
if ($LASTEXITCODE -ne 0 -or -not (Test-Path "dist\LockIt\LockIt.exe")) {
    throw "PyInstaller build failed: dist\LockIt\LockIt.exe was not created."
}

Write-Host "[4/5] Checking Inno Setup 6..." -ForegroundColor Cyan
function Find-Iscc {
    $paths = @(
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
        "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
    )
    foreach ($p in $paths) { if ($p -and (Test-Path $p)) { return $p } }
    $cmd = Get-Command ISCC.exe -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    return $null
}

$iscc = Find-Iscc
if (-not $iscc) {
    Write-Host "Inno Setup 6 was not found. Installing it automatically..." -ForegroundColor Yellow
    $winget = Ensure-Winget
    & $winget install --id JRSoftware.InnoSetup -e --silent --accept-package-agreements --accept-source-agreements --disable-interactivity
    if ($LASTEXITCODE -ne 0) {
        throw "Automatic Inno Setup installation failed (winget exit code $LASTEXITCODE)."
    }
    Refresh-Path
    Start-Sleep -Seconds 2
    $iscc = Find-Iscc
    if (-not $iscc) { throw "Inno Setup 6 was installed but ISCC.exe could not be located." }
}
Write-Host "Using: $iscc" -ForegroundColor DarkGray

Write-Host "[5/5] Building Windows installer..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force "installer_output" | Out-Null
& $iscc "installer\LockIt.iss"
if ($LASTEXITCODE -ne 0) { throw "Inno Setup build failed." }

$setup = Get-ChildItem "installer_output\LockIt-Setup-*.exe" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $setup) { throw "Installer build failed: setup EXE was not created." }

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host " READY: LockIt Windows installer was built " -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host "Installer: $($setup.FullName)" -ForegroundColor Green
Write-Host ""
Start-Process explorer.exe "/select,`"$($setup.FullName)`""
