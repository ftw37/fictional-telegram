param(
 [string]$DevelopmentRoot = "$([Environment]::GetFolderPath('MyDocuments'))/Codex/HTL-Development",
 [string]$ToolsRoot = "$([Environment]::GetFolderPath('MyDocuments'))/Codex/DevTools/htl"
)
$ErrorActionPreference='Stop'
. "$PSScriptRoot/Enter-BuildEnvironment.ps1" -ToolsRoot $ToolsRoot
$source=Join-Path $DevelopmentRoot 'integration-020'
$output=Join-Path $DevelopmentRoot 'build/audio-tests'
New-Item -ItemType Directory -Path $output -Force | Out-Null
$common=@('/nologo','/std:c++20','/EHsc','/MD','/O2','-fuse-ld=lld',"/winsysroot$sdkRoot","/I$source/src")
& clang-cl @common "$PSScriptRoot/../tests/audio_safety_smoke.cpp" "/Fo$output/audio_safety.obj" "/Fe$output/audio_safety.exe"
if($LASTEXITCODE -ne 0){throw 'Audio safety checks did not compile'}
& "$output/audio_safety.exe"
if($LASTEXITCODE -ne 0){throw 'Audio safety checks failed'}
& clang-cl @common "/I$DevelopmentRoot/build/integration-020/_deps/fmt-src/include" "$PSScriptRoot/../tests/spatial_audio_smoke.cpp" "$source/src/core/libraries/audio3d/audio3d_spatializer.cpp" "/Fo$output/" "/Fe$output/spatial_audio.exe"
if($LASTEXITCODE -ne 0){throw 'Spatial checks did not compile'}
& "$output/spatial_audio.exe"
if($LASTEXITCODE -ne 0){throw 'Spatial checks failed'}
Write-Output 'Audio overload, stereo symmetry, spatial direction, silence and invalid-sample checks passed.'
