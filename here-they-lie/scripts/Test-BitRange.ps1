param(
 [string]$DevelopmentRoot = "$([Environment]::GetFolderPath('MyDocuments'))/Codex/HTL-Development",
 [string]$ToolsRoot = "$([Environment]::GetFolderPath('MyDocuments'))/Codex/DevTools/htl"
)
$ErrorActionPreference='Stop'
. "$PSScriptRoot/Enter-BuildEnvironment.ps1" -ToolsRoot $ToolsRoot
$source=Join-Path $DevelopmentRoot 'AstroQuest/shadps4-arm64-main'
$test=Join-Path $DevelopmentRoot 'bit-range-test.exe'
& clang-cl /nologo /std:c++20 /EHsc /MD -fuse-ld=lld "/winsysroot$sdkRoot" "/I$source/src" "/I$source/externals/spdlog/include" "/I$source/externals/fmt/include" "$PSScriptRoot/../tests/bit_range_smoke.cpp" "/Fo$DevelopmentRoot/bit-range-test.obj" "/Fe$test" /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'Could not compile bit range checks.'}
& $test
if($LASTEXITCODE -ne 0){throw 'Bit range checks failed.'}
