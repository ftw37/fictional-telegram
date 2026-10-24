param(
 [string]$DevelopmentRoot = "$([Environment]::GetFolderPath('MyDocuments'))/Codex/HTL-Development",
 [string]$ToolsRoot = "$([Environment]::GetFolderPath('MyDocuments'))/Codex/DevTools/htl",
 [string]$Python = "$env:USERPROFILE/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe",
 [int]$Jobs = 8,
 [switch]$ConfigureOnly
)
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot/Enter-BuildEnvironment.ps1" -ToolsRoot $ToolsRoot
$lock = Get-Content "$PSScriptRoot/../upstream-020.lock.json" -Raw | ConvertFrom-Json
$source = Join-Path $DevelopmentRoot 'integration-020'
$build = Join-Path $DevelopmentRoot 'build/integration-020'
$patch = (Resolve-Path "$PSScriptRoot/../patches/htl-shadps4-020-integration.patch").Path
if (-not (Test-Path "$source/.git")) {
 if (Test-Path $source) { throw 'The source folder already exists without Git; left untouched.' }
 & git clone --filter=blob:none --no-checkout $lock.repository $source
 if ($LASTEXITCODE -ne 0) { throw 'Official source clone failed' }
 & git -C $source config core.longpaths true
 & git -C $source checkout --detach $lock.commit
 if ($LASTEXITCODE -ne 0) { throw 'Pinned source checkout failed' }
}
if ((& git -C $source rev-parse HEAD) -ne $lock.commit) { throw 'Unexpected source revision; left untouched.' }
$dependencySource = $source
$externals = Get-Item -LiteralPath (Join-Path $source 'externals') -ErrorAction SilentlyContinue
if ($externals -and ($externals.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
 $dependencySource = Join-Path $DevelopmentRoot 'upstream-shadps4'
 $expectedTarget = [IO.Path]::GetFullPath((Join-Path $dependencySource 'externals'))
 $actualTarget = [IO.Path]::GetFullPath([string]$externals.Target)
 if ($actualTarget -ine $expectedTarget) { throw 'Unexpected dependency junction; left untouched.' }
 if ((& git -C $dependencySource rev-parse HEAD) -ne $lock.commit) { throw 'Unexpected dependency owner revision' }
}
& git -C $dependencySource submodule update --init --recursive --jobs 6
if ($LASTEXITCODE -ne 0) { throw 'Dependency checkout failed' }
$sdk = Join-Path $source 'externals/openxr-sdk'
if (-not (Test-Path "$sdk/CMakeLists.txt")) {
 $astro = Join-Path $DevelopmentRoot 'AstroQuest'
 if (-not (Test-Path "$astro/.git")) { & "$PSScriptRoot/Get-EmulatorSource.ps1" -DevelopmentRoot $DevelopmentRoot -ToolsRoot $ToolsRoot }
 if ((& git -C $astro rev-parse HEAD) -ne $lock.vr_source_commit) { throw 'Unexpected OpenXR donor revision' }
 Copy-Item -LiteralPath (Join-Path $astro $lock.openxr_vendored_path) -Destination $sdk -Recurse
}
& git -C $source apply --reverse --check $patch 2>$null
if ($LASTEXITCODE -ne 0) {
 & git -C $source apply --check $patch
 if ($LASTEXITCODE -ne 0) { throw 'Integration patch conflicts with source changes; left untouched.' }
 & git -C $source apply $patch
 if ($LASTEXITCODE -ne 0) { throw 'Could not apply integration patch' }
}
if (-not (Test-Path $Python)) { throw 'Pass -Python with a Python 3 executable path.' }
& cmake -S $source -B $build -G Ninja '-DCMAKE_BUILD_TYPE=Release' '-DCMAKE_TRY_COMPILE_CONFIGURATION=Release' '-DCMAKE_C_COMPILER=clang-cl' '-DCMAKE_CXX_COMPILER=clang-cl' '-DCMAKE_LINKER=lld-link' '-DCMAKE_RC_COMPILER=llvm-rc' '-DCMAKE_MT=llvm-mt' "-DCMAKE_C_FLAGS_INIT=/winsysroot $sdkRoot" "-DCMAKE_CXX_FLAGS_INIT=/winsysroot $sdkRoot" '-DCMAKE_POLICY_VERSION_MINIMUM=3.5' '-DENABLE_DISCORD_RPC=OFF' '-DENABLE_UPDATER=OFF' '-DENABLE_OPENXR=ON' '-DALSOFT_UPDATE_BUILD_VERSION=OFF' "-DPython3_EXECUTABLE=$Python"
if ($LASTEXITCODE -ne 0) { throw 'Configure failed' }
if (-not $ConfigureOnly) {
 & cmake --build $build --target shadps4 --parallel $Jobs
 if ($LASTEXITCODE -ne 0) { throw 'Build failed' }
 Write-Output "Experimental emulator built: $build/shadps4.exe. Normal launchers were not changed."
}
