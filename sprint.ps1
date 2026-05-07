#Requires -Version 5.1
<#
.SYNOPSIS
    Orchestrateur sprint MCP server template v0.1.0 (J13-J15).
.DESCRIPTION
    Subcommands:
        preflight  - Install deps + verify imports + check Python >=3.11
        status     - Verdict cut-decision (tools/resources/prompts/tests)
        commit     - Atomic commit: ruff + mypy + pytest + git add/commit/push
        ship       - Integration tests + Quickstart e2e on clean dir + tag v0.1.0
.EXAMPLE
    .\sprint.ps1 preflight
.EXAMPLE
    .\sprint.ps1 commit "feat: add Tool #2 search_recipes"
.EXAMPLE
    .\sprint.ps1 ship
.NOTES
    Repo: claude-mcp-server-template
    Dependencies: uv, git, Python >=3.11
#>
param(
    [Parameter(Mandatory=$true, Position=0)]
    [ValidateSet("preflight", "status", "commit", "ship")]
    [string]$Command,

    [Parameter(Position=1)]
    [string]$Message
)

$ErrorActionPreference = "Stop"

function Invoke-Preflight {
    Write-Host "=== Pre-flight gate ===" -ForegroundColor Cyan

    Write-Host "[1/3] Installing runtime deps..." -ForegroundColor Yellow
    uv add 'fastmcp[tasks]>=3.0' 'pydantic-settings>=2.0' 'tenacity>=9.0' `
           'opentelemetry-api>=1.20.0' 'opentelemetry-sdk>=1.20.0' `
           'opentelemetry-exporter-otlp-proto-http>=1.20.0' `
           'opentelemetry-instrumentation-httpx>=0.50b0' `
           'fastapi>=0.115' 'uvicorn>=0.30' 'httpx>=0.27'
    if ($LASTEXITCODE -ne 0) {
        Write-Host "FAIL: uv add (runtime)" -ForegroundColor Red
        Write-Host "Mitigation possible: Cyclopts v4 docutils issue -> uv add 'cyclopts>=5.0.0a1'" -ForegroundColor Yellow
        exit 1
    }

    Write-Host "[2/3] Installing dev deps..." -ForegroundColor Yellow
    uv add --dev 'pytest>=8.0' 'pytest-asyncio>=0.23' 'ruff>=0.5' 'mypy>=1.10'
    if ($LASTEXITCODE -ne 0) {
        Write-Host "FAIL: uv add (dev)" -ForegroundColor Red
        exit 1
    }

    Write-Host "[3/3] Import smoke test..." -ForegroundColor Yellow
    $smokeTest = @'
import sys
assert sys.version_info >= (3, 11), f"Python 3.11+ required, got {sys.version_info}"
from pydantic_settings import BaseSettings
from fastmcp import FastMCP, Context
from tenacity import AsyncRetrying
import mcp
print(f"Python={sys.version.split()[0]}")
print(f"mcp={mcp.__version__}")
print("Pre-flight OK")
'@
    uv run python -c $smokeTest
    if ($LASTEXITCODE -ne 0) {
        Write-Host "FAIL: import smoke test" -ForegroundColor Red
        exit 1
    }

    Write-Host "=== Pre-flight GO -- sprint J13 14h cleared ===" -ForegroundColor Green
    exit 0
}

function Invoke-Status {
    Write-Host "=== Sprint status ===" -ForegroundColor Cyan

    if (-not (Test-Path "tools/cut-decision.py")) {
        Write-Host "FAIL: tools/cut-decision.py missing" -ForegroundColor Red
        exit 1
    }

    uv run python tools/cut-decision.py
    $verdictExitCode = $LASTEXITCODE

    Write-Host ""
    $branch = git status --short --branch | Select-Object -First 1
    Write-Host "Git: $branch"
    $lastCommit = git log -1 --format="%cr -- %s"
    Write-Host "Last commit: $lastCommit"

    exit $verdictExitCode
}

function Invoke-Commit {
    if (-not $Message) {
        Write-Host "Usage: .\sprint.ps1 commit ""message""" -ForegroundColor Red
        exit 1
    }

    Write-Host "=== Atomic commit ===" -ForegroundColor Cyan

    Write-Host "[1/4] ruff check..." -ForegroundColor Yellow
    uv run ruff check src/ tests/
    if ($LASTEXITCODE -ne 0) { Write-Host "FAIL: ruff" -ForegroundColor Red; exit 1 }

    Write-Host "[2/4] mypy..." -ForegroundColor Yellow
    uv run mypy src/
    if ($LASTEXITCODE -ne 0) { Write-Host "FAIL: mypy" -ForegroundColor Red; exit 1 }

    Write-Host "[3/4] pytest..." -ForegroundColor Yellow
    uv run pytest -q
    if ($LASTEXITCODE -ne 0) { Write-Host "FAIL: pytest" -ForegroundColor Red; exit 1 }

    Write-Host "[4/4] git commit + push..." -ForegroundColor Yellow
    git add -A
    git commit -m $Message
    if ($LASTEXITCODE -ne 0) { Write-Host "FAIL: git commit (nothing to commit?)" -ForegroundColor Red; exit 1 }
    git push
    if ($LASTEXITCODE -ne 0) { Write-Host "FAIL: git push" -ForegroundColor Red; exit 1 }

    Write-Host "=== Commit OK ===" -ForegroundColor Green
}

function Invoke-Ship {
    Write-Host "=== SHIP v0.1.0 ===" -ForegroundColor Cyan

    Write-Host "[1/4] Integration tests..." -ForegroundColor Yellow
    uv run pytest tests/integration/ -v
    if ($LASTEXITCODE -ne 0) { Write-Host "FAIL: integration tests" -ForegroundColor Red; exit 1 }

    Write-Host "[2/4] Quickstart e2e clean install..." -ForegroundColor Yellow
    $cleanDir = "$env:TEMP\mcp-quickstart-test-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    $repoRoot = (Get-Location).Path
    New-Item -ItemType Directory -Path $cleanDir -Force | Out-Null
    Push-Location $cleanDir
    try {
        git clone $repoRoot . 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) { Write-Host "FAIL: git clone" -ForegroundColor Red; exit 1 }
        uv sync 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) { Write-Host "FAIL: uv sync" -ForegroundColor Red; exit 1 }
        Write-Host "Clean clone + sync OK in $cleanDir" -ForegroundColor Green
        Write-Host "MANUAL CHECK: run README quickstart commands here, verify server starts." -ForegroundColor Cyan
        Write-Host "Press ENTER once Quickstart manual validation done (or Ctrl+C to abort)..." -ForegroundColor Yellow
        Read-Host
    } finally {
        Pop-Location
    }

    Write-Host "[3/4] Tag v0.1.0..." -ForegroundColor Yellow
    git tag -a v0.1.0 -m "Release v0.1.0 -- first ship"
    if ($LASTEXITCODE -ne 0) { Write-Host "FAIL: git tag" -ForegroundColor Red; exit 1 }
    git push origin v0.1.0
    if ($LASTEXITCODE -ne 0) { Write-Host "FAIL: git push tag" -ForegroundColor Red; exit 1 }

    Write-Host "[4/4] Cleanup test dir..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $cleanDir -ErrorAction SilentlyContinue

    Write-Host "=== SHIPPED v0.1.0 ===" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps (post-ship):" -ForegroundColor Cyan
    Write-Host "  1. Submit Catalog Upwork (marketing/post-ship-bundle.md sec.1)"
    Write-Host "  2. Schedule dev.to publish J17 morning (marketing/post-ship-bundle.md sec.2)"
    Write-Host "  3. Schedule Twitter thread J17 (marketing/post-ship-bundle.md sec.3)"
    Write-Host "  4. r/mcp post J17 PM if Twitter traction OK (marketing/post-ship-bundle.md sec.4)"
}

switch ($Command) {
    "preflight" { Invoke-Preflight }
    "status"    { Invoke-Status }
    "commit"    { Invoke-Commit }
    "ship"      { Invoke-Ship }
}
