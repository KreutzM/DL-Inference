param(
    [string]$Url = 'http://localhost:8001/health'
)
$ErrorActionPreference = 'Stop'
python -m repo2ctl.cli health --url $Url
