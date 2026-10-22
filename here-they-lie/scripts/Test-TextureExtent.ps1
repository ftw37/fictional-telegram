param(
 [string]$DevelopmentRoot = "$([Environment]::GetFolderPath('MyDocuments'))/Codex/HTL-Development",
 [string]$ToolsRoot = "$([Environment]::GetFolderPath('MyDocuments'))/Codex/DevTools/htl"
)
$ErrorActionPreference='Stop'
. "$PSScriptRoot/Enter-BuildEnvironment.ps1" -ToolsRoot $ToolsRoot
$source=Join-Path $DevelopmentRoot 'AstroQuest/shadps4-arm64-main'
$test=Join-Path $DevelopmentRoot 'texture-extent-test.exe'
& clang-cl /nologo /std:c++20 /EHsc /MD -fuse-ld=lld "/winsysroot$sdkRoot" "/I$source/src" "/I$source/externals/spdlog/include" "/I$source/externals/fmt/include" "$PSScriptRoot/../tests/texture_extent_smoke.cpp" "/Fo$DevelopmentRoot/texture-extent-test.obj" "/Fe$test" /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'Could not compile texture extent checks.'}
& $test
if($LASTEXITCODE -ne 0){throw 'Texture extent checks failed.'}
