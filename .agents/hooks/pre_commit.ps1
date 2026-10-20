$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
Set-Location $repoRoot

# Whitespace/conflict-marker checks on the staged diff.
git diff --cached --check
if ($LASTEXITCODE -ne 0) { throw 'git diff --cached --check failed.' }

$staged = @(git diff --cached --name-only --diff-filter=ACMR)
if ($LASTEXITCODE -ne 0) { throw 'Unable to inspect staged filenames.' }
$blockedExtensions = @('.ckpt', '.pt', '.pth', '.onnx', '.safetensors', '.engine', '.gguf')
$blockedNames = @('.env', '.env.local', '.env.production', 'id_rsa', 'id_ed25519')
$problems = New-Object System.Collections.Generic.List[string]
foreach ($relative in $staged) {
    if ([string]::IsNullOrWhiteSpace($relative)) { continue }
    $name = [IO.Path]::GetFileName($relative)
    $ext = [IO.Path]::GetExtension($relative).ToLowerInvariant()
    if ($blockedNames -contains $name -or $name -match '^\.env\.(?!example$)') {
        $problems.Add("Potential secret/environment file staged: $relative")
    }
    if ($blockedExtensions -contains $ext) {
        $problems.Add("Model/engine binary should not be committed by default: $relative")
    }
    $absolute = Join-Path $repoRoot $relative
    if (Test-Path -LiteralPath $absolute -PathType Leaf) {
        $length = (Get-Item -LiteralPath $absolute).Length
        if ($length -gt 50MB) { $problems.Add("File exceeds 50 MiB; verify it is not a generated/user asset: $relative ($length bytes)") }
        if ($ext -in @('.py', '.js', '.ts', '.json', '.yaml', '.yml', '.md', '.toml', '.ps1', '.sh')) {
            $content = Get-Content -LiteralPath $absolute -Raw -ErrorAction SilentlyContinue
            if ($content -match '(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*["'']?(sk-[A-Za-z0-9_-]{16,}|AIza[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,})') {
                $problems.Add("Possible hard-coded credential in: $relative")
            }
        }
    }
}
if ($problems.Count -gt 0) {
    Write-Host 'Pre-commit guard blocked this commit:' -ForegroundColor Red
    $problems | ForEach-Object { Write-Host " - $_" -ForegroundColor Red }
    Write-Host 'Remove secrets/binaries or explicitly review the rule before committing.'
    exit 1
}
Write-Host 'Pre-commit guard passed.' -ForegroundColor Green
exit 0
