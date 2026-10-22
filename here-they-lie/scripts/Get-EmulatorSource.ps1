param(
 [string]$DevelopmentRoot = "$([Environment]::GetFolderPath('MyDocuments'))/Codex/HTL-Development",
 [string]$ToolsRoot = "$([Environment]::GetFolderPath('MyDocuments'))/Codex/DevTools/htl"
)
$ErrorActionPreference = 'Stop'
$git = "$ToolsRoot/git/cmd/git.exe"
$lock = Get-Content "$PSScriptRoot/../upstream.lock.json" -Raw | ConvertFrom-Json
$checkout = Join-Path $DevelopmentRoot 'AstroQuest'
if (-not (Test-Path "$checkout/.git")) {
 & $git clone --filter=blob:none --no-checkout $lock.repository $checkout
 if ($LASTEXITCODE -ne 0) { throw 'Clone failed' }
 & $git -C $checkout config core.longpaths true
 & $git -C $checkout checkout --detach $lock.commit
 if ($LASTEXITCODE -ne 0) { throw 'Pinned checkout failed' }
} elseif ((& $git -C $checkout rev-parse HEAD) -ne $lock.commit) {
 throw 'Existing source is on a different revision; left untouched.'
}
& $git -C $checkout submodule update --init --jobs 6
if ($LASTEXITCODE -ne 0) { throw 'Dependency checkout failed' }
& $git -C $checkout submodule update --init --recursive -- shadps4-arm64-main/externals/zydis shadps4-arm64-main/externals/freetype
if ($LASTEXITCODE -ne 0) { throw 'Nested dependency checkout failed' }
