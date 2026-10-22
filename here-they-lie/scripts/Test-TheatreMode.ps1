param(
 [string]$DevelopmentRoot = "$([Environment]::GetFolderPath('MyDocuments'))/Codex/HTL-Development",
 [string]$ToolsRoot = "$([Environment]::GetFolderPath('MyDocuments'))/Codex/DevTools/htl"
)
$ErrorActionPreference='Stop'
. "$PSScriptRoot/Enter-BuildEnvironment.ps1" -ToolsRoot $ToolsRoot
$source=Join-Path $DevelopmentRoot 'AstroQuest/shadps4-arm64-main'
$test=Join-Path $DevelopmentRoot 'theatre-mode-test.exe'
& clang-cl /nologo /std:c++20 /EHsc /MD -fuse-ld=lld "/winsysroot$sdkRoot" "/I$source/src" "$PSScriptRoot/../tests/theatre_mode_smoke.cpp" "/Fo$DevelopmentRoot/theatre-mode-test.obj" "/Fe$test" /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'Could not compile theatre-mode checks.'}
$previous=$env:SHADPS4_HTL_THEATRE
try {
 foreach($mode in '0','1') {
  $env:SHADPS4_HTL_THEATRE=$mode
  & $test
  if($LASTEXITCODE -ne 0){throw 'Theatre-mode checks failed.'}
 }
} finally {$env:SHADPS4_HTL_THEATRE=$previous}
