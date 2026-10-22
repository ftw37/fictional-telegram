param(
 [string]$DevelopmentRoot = "$([Environment]::GetFolderPath('MyDocuments'))/Codex/HTL-Development",
 [string]$ToolsRoot = "$([Environment]::GetFolderPath('MyDocuments'))/Codex/DevTools/htl"
)
$ErrorActionPreference='Stop'
. "$PSScriptRoot/Enter-BuildEnvironment.ps1" -ToolsRoot $ToolsRoot
$source=Join-Path $DevelopmentRoot 'AstroQuest/shadps4-arm64-main'
$test=Join-Path $DevelopmentRoot 'startup-calibration-test.exe'
& clang-cl /nologo /std:c++20 /EHsc /MD -fuse-ld=lld "/winsysroot$sdkRoot" "/I$source/src" "$PSScriptRoot/../tests/startup_calibration_smoke.cpp" "/Fo$DevelopmentRoot/startup-calibration-test.obj" "/Fe$test" /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'Could not compile startup calibration checks.'}
& $test
if($LASTEXITCODE -ne 0){throw 'Startup calibration checks failed.'}
