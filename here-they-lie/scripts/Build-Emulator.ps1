param(
 [string]$DevelopmentRoot = "$([Environment]::GetFolderPath('MyDocuments'))/Codex/HTL-Development",
 [string]$ToolsRoot = "$([Environment]::GetFolderPath('MyDocuments'))/Codex/DevTools/htl",
 [int]$Jobs = 8,
 [switch]$ConfigureOnly
)
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot/Enter-BuildEnvironment.ps1" -ToolsRoot $ToolsRoot
$source = Join-Path $DevelopmentRoot 'AstroQuest/shadps4-arm64-main'
$build = Join-Path $DevelopmentRoot 'build/win-x64'
$lock = Get-Content "$PSScriptRoot/../upstream.lock.json" -Raw | ConvertFrom-Json
$actual = & git -C (Split-Path $source) rev-parse HEAD
if ($LASTEXITCODE -ne 0 -or $actual -ne $lock.commit) { throw 'Source revision does not match upstream.lock.json' }
Push-Location (Split-Path $source)
try {
& cmake -S $source -B $build -G Ninja '-DCMAKE_BUILD_TYPE=Release' '-DCMAKE_TRY_COMPILE_CONFIGURATION=Release' '-DCMAKE_C_COMPILER=clang-cl' '-DCMAKE_CXX_COMPILER=clang-cl' '-DCMAKE_LINKER=lld-link' '-DCMAKE_RC_COMPILER=llvm-rc' '-DCMAKE_MT=llvm-mt' "-DCMAKE_C_FLAGS_INIT=/winsysroot $sdkRoot" "-DCMAKE_CXX_FLAGS_INIT=/winsysroot $sdkRoot" '-DCMAKE_POLICY_VERSION_MINIMUM=3.5' '-DENABLE_DISCORD_RPC=OFF' '-DENABLE_UPDATER=OFF' '-DENABLE_OPENXR=ON'
if ($LASTEXITCODE -ne 0) { throw 'CMake configure failed' }
if (-not $ConfigureOnly) {
 & cmake --build $build --target shadps4 --parallel $Jobs
 if ($LASTEXITCODE -ne 0) { throw 'Emulator build failed' }
 Write-Output "Built emulator: $build/shadps4.exe"
}
} finally { Pop-Location }
