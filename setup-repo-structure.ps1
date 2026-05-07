#Requires -Version 5.1
<#
.SYNOPSIS
    One-shot setup repo structure pour sprint MCP server template v0.1.0.
.DESCRIPTION
    Cree les dossiers src/, tests/, tasks/ + __init__.py + skeletons (server.py, test_smoke.py)
    pour que .\sprint.ps1 commit ne plante pas au premier coup (ruff/mypy/pytest s'attendent
    a src/ et tests/).
    Idempotent: safe a re-run, ne casse pas l'existant.
.NOTES
    A lancer UNE FOIS avant le sprint J13 14h, apres .\sprint.ps1 preflight.
#>

$ErrorActionPreference = "Stop"

Write-Host "=== Setup repo structure ===" -ForegroundColor Cyan

$dirs = @(
    "src",
    "src/tools",
    "src/resources",
    "src/prompts",
    "tests",
    "tests/unit",
    "tests/integration",
    "tasks"
)
foreach ($d in $dirs) {
    New-Item -ItemType Directory -Path $d -Force | Out-Null
    Write-Host "  [DIR]  $d" -ForegroundColor Green
}

$initFiles = @(
    "src/__init__.py",
    "src/tools/__init__.py",
    "src/resources/__init__.py",
    "src/prompts/__init__.py",
    "tests/__init__.py",
    "tests/unit/__init__.py",
    "tests/integration/__init__.py"
)
foreach ($f in $initFiles) {
    if (-not (Test-Path $f)) {
        New-Item -ItemType File -Path $f | Out-Null
        Write-Host "  [INIT] $f" -ForegroundColor Green
    } else {
        Write-Host "  [SKIP] $f (existe deja)" -ForegroundColor DarkGray
    }
}

$serverPy = @'
"""MCP server entry point -- to be implemented J13 14h+."""
from fastmcp import FastMCP

mcp = FastMCP("PantryMCP")

# Tools/Resources/Prompts registration happens here:
# from src.tools import get_recipe, search_recipes, update_pantry, generate_meal_plan
# get_recipe.register(mcp)
# search_recipes.register(mcp)
# update_pantry.register(mcp)
# generate_meal_plan.register(mcp)

if __name__ == "__main__":
    mcp.run()
'@

$testSmoke = @'
"""Smoke test -- guarantees pytest discovery + sprint.ps1 commit pipeline works.

Will be replaced/expanded J13 14h+ as actual tests are written for config.py,
pantry_client.py, and Tool #1 get_recipe.
"""


def test_smoke() -> None:
    """Trivial test to keep pytest green during sprint setup phase."""
    assert True
'@

$skeletons = @{
    "src/server.py" = $serverPy
    "tests/unit/test_smoke.py" = $testSmoke
}

foreach ($pair in $skeletons.GetEnumerator()) {
    $path = $pair.Key
    $needsCreate = (-not (Test-Path $path)) -or ((Get-Item $path).Length -eq 0)
    if ($needsCreate) {
        $pair.Value | Out-File -FilePath $path -Encoding utf8 -NoNewline
        Write-Host "  [SKEL] $path" -ForegroundColor Green
    } else {
        Write-Host "  [SKIP] $path (existe non-vide)" -ForegroundColor DarkGray
    }
}

$pyprojectPath = "pyproject.toml"
$pyprojectContent = if (Test-Path $pyprojectPath) { Get-Content $pyprojectPath -Raw } else { "" }
$ruffConfigBlock = @"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "B", "UP"]
ignore = ["E501"]

[tool.mypy]
python_version = "3.11"
strict = false
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
"@

if ($pyprojectContent -notmatch '\[tool\.ruff\]') {
    Add-Content -Path $pyprojectPath -Value $ruffConfigBlock
    Write-Host "  [CFG]  ruff/mypy/pytest config appended to pyproject.toml" -ForegroundColor Green
} else {
    Write-Host "  [SKIP] pyproject.toml has [tool.ruff] already" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "=== Structure ready ===" -ForegroundColor Green
