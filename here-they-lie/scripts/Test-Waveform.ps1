param(
 [string]$DevelopmentRoot = "$([Environment]::GetFolderPath('MyDocuments'))/Codex/HTL-Development",
 [string]$ToolsRoot = "$([Environment]::GetFolderPath('MyDocuments'))/Codex/DevTools/htl"
)
$ErrorActionPreference='Stop'
. "$PSScriptRoot/Enter-BuildEnvironment.ps1" -ToolsRoot $ToolsRoot
$source=Join-Path $DevelopmentRoot 'AstroQuest/shadps4-arm64-main'
$test=Join-Path $DevelopmentRoot 'waveform-test.exe'
& clang-cl /nologo /std:c++20 /EHsc /MD -fuse-ld=lld "/winsysroot$sdkRoot" "/I$source/src" "/I$source/externals/LibAtrac9/C/src" "$PSScriptRoot/../tests/waveform_smoke.cpp" "/Fo$DevelopmentRoot/waveform-test.obj" "/Fe$test" /link "$DevelopmentRoot/build/win-x64/externals/LibAtrac9.lib" /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'Could not compile the waveform checks.'}
& $test
if($LASTEXITCODE -ne 0){throw 'Waveform checks failed.'}
