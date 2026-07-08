param(
    [switch]$Send,
    [switch]$SampleData,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot
$env:PYTHONPATH = Join-Path $ProjectRoot "src"

$argsList = @(
    "-m", "stock_info.cli",
    "--config", "config/us_report.toml"
)

if ($Send) { $argsList += "--send" } else { $argsList += "--dry-run" }
if ($SampleData) { $argsList += "--sample-data" }
if ($Force) { $argsList += "--force" }

python @argsList
