param(
    [string]$Service
)
$ErrorActionPreference = 'Stop'
if ($Service) {
    python -m repo2ctl.cli logs $Service
} else {
    python -m repo2ctl.cli logs
}
