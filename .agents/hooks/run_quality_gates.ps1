param([switch]$SkipBackend, [switch]$SkipFrontend)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
Set-Location $root
$failed = New-Object System.Collections.Generic.List[string]

# Detect Python executable (supports py launcher, custom env var, or python in PATH)
$pythonCmd = if ($env:PYTHON_EXECUTABLE) { $env:PYTHON_EXECUTABLE }
elseif (Get-Command py -ErrorAction SilentlyContinue) { "py" }
else { "python" }

Write-Host '== Agent harness validation ==' -ForegroundColor Cyan
& $pythonCmd .agents/hooks/validate_agent_assets.py
if ($LASTEXITCODE -ne 0) { $failed.Add('agent assets validation') }

if (-not $SkipBackend) {
    if (Test-Path 'backend/tests') {
        Write-Host '== Backend pytest ==' -ForegroundColor Cyan
        $oldPythonPath = $env:PYTHONPATH
        $env:PYTHONPATH = 'backend/src' + $(if ($oldPythonPath) { ";$oldPythonPath" } else { '' })
        & $pythonCmd -m pytest backend/tests -v
        if ($LASTEXITCODE -ne 0) { $failed.Add('backend pytest') }
        $env:PYTHONPATH = $oldPythonPath
    } else { Write-Host 'Backend test directory not found; skipped.' -ForegroundColor Yellow }
}

if (-not $SkipFrontend) {
    if (Test-Path 'frontend/package.json') {
        if (-not (Test-Path 'frontend/node_modules')) {
            Write-Host 'Frontend dependencies missing; run npm install in frontend/ before frontend gates.' -ForegroundColor Yellow
            $failed.Add('frontend dependencies missing')
        } else {
            Push-Location 'frontend'
            Write-Host '== Frontend tests ==' -ForegroundColor Cyan
            npm test
            if ($LASTEXITCODE -ne 0) { $failed.Add('frontend tests') }
            Write-Host '== Frontend production build ==' -ForegroundColor Cyan
            npm run build
            if ($LASTEXITCODE -ne 0) { $failed.Add('frontend build') }
            Pop-Location
        }
    } else { Write-Host 'Frontend package.json not found; skipped.' -ForegroundColor Yellow }
}

Write-Host '== Git whitespace check ==' -ForegroundColor Cyan
git diff --check
if ($LASTEXITCODE -ne 0) { $failed.Add('git diff --check') }

if ($failed.Count -gt 0) {
    Write-Host 'Quality gates failed or were blocked:' -ForegroundColor Red
    $failed | ForEach-Object { Write-Host " - $_" -ForegroundColor Red }
    exit 1
}
Write-Host 'All available quality gates passed.' -ForegroundColor Green
exit 0
