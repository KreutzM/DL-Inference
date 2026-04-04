param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ArgsList
)

$ErrorActionPreference = 'Stop'
python -m repo2ctl.cli @ArgsList
