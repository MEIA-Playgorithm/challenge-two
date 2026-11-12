# Rebuild data/csv/ from the zip parts in data/archive/.
# Usage (from the repo root): pwsh data/unzip.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$zip = Join-Path $PSScriptRoot "csv.zip"
$out = [System.IO.File]::Create($zip)
Get-ChildItem archive/csv.zip.part* | Sort-Object Name | ForEach-Object {
    $in = [System.IO.File]::OpenRead($_.FullName)
    $in.CopyTo($out)
    $in.Close()
}
$out.Close()

Expand-Archive -Path $zip -DestinationPath $PSScriptRoot -Force
Remove-Item $zip
Write-Host "Done: data/csv/"
