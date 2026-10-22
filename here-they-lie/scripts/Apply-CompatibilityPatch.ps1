param(
 [string]$DevelopmentRoot = "$([Environment]::GetFolderPath('MyDocuments'))/Codex/HTL-Development",
 [string]$ToolsRoot = "$([Environment]::GetFolderPath('MyDocuments'))/Codex/DevTools/htl"
)
$ErrorActionPreference = 'Stop'
$git = Join-Path $ToolsRoot 'git/cmd/git.exe'
$checkout = Join-Path $DevelopmentRoot 'AstroQuest'
$patch = (Resolve-Path "$PSScriptRoot/../patches/htl-compatibility.patch").Path
$lock = Get-Content "$PSScriptRoot/../upstream.lock.json" -Raw | ConvertFrom-Json
$actual = & $git -C $checkout rev-parse HEAD
if ($LASTEXITCODE -ne 0 -or $actual -ne $lock.commit) {
 throw 'Source revision does not match upstream.lock.json. No files were changed.'
}
& $git -C $checkout apply --reverse --check $patch 2>$null
if ($LASTEXITCODE -eq 0) {
 Write-Output 'The compatibility patch is already applied.'
 exit 0
}
& $git -C $checkout apply --check $patch
if ($LASTEXITCODE -ne 0) {
 throw 'The patch conflicts with local source changes. No files were changed.'
}
& $git -C $checkout apply $patch
if ($LASTEXITCODE -ne 0) { throw 'Could not apply the compatibility patch.' }
Write-Output 'Applied the Here They Lie compatibility patch. Build-Emulator.ps1 can now rebuild it.'
