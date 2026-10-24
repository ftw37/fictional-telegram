param(
 [string]$DevelopmentRoot = "$HOME/Documents/Codex/HTL-Development",
 [string]$RuntimeRoot = "$HOME/Documents/Codex/HTL-Development/experiments/stable020-a",
 [string]$Python = "$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe",
 [string]$Game = "$HOME/Documents/Codex/HTL-Test/no-vignette-v1/uroot"
)
$ErrorActionPreference = 'Stop'
$runtime = [IO.Path]::GetFullPath($RuntimeRoot)
$destination = [IO.Path]::GetFullPath((Join-Path $DevelopmentRoot 'test-vr'))
$launcher = Join-Path $PSScriptRoot 'launch_here_they_lie.py'
$exe = Join-Path $runtime 'test-vr/shadps4.exe'
foreach ($required in @($Python, $launcher, $exe, (Join-Path $Game 'eboot.bin'))) {
 if (-not (Test-Path -LiteralPath $required -PathType Leaf)) { throw "Missing prerequisite: $required" }
}
$config = Get-Content -LiteralPath (Join-Path $runtime 'test-vr/user/config.json') -Raw | ConvertFrom-Json
if ($config.GPU.readbacks_mode -ne 1) { throw 'Candidate must use relaxed GPU readbacks.' }
if ($config.Vulkan.vkvalidation_enabled) { throw 'Turn off diagnostic validation before installing normal launchers.' }
$evidence = Get-Content -LiteralPath (Join-Path $runtime 'candidate-evidence.json') -Raw | ConvertFrom-Json
if ($null -eq $evidence.pipeline_cache_enabled -or
    $config.Vulkan.pipeline_cache_enabled -ne $evidence.pipeline_cache_enabled) {
 throw 'Current pipeline-cache setting differs from the recorded candidate.'
}
if ((Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash -ine $evidence.emulator_sha256) {
 throw 'Candidate executable differs from the recorded route tests.'
}
if (@($evidence.successful_routes).Count -lt 3) { throw 'Record three successful route repetitions first.' }
foreach ($run in $evidence.successful_routes) {
 if ($run -notmatch '^[a-zA-Z0-9_-]+$') { throw 'Invalid route label.' }
 $folder = Join-Path $runtime "performance-runs/$run"
 $result = Get-Content -LiteralPath (Join-Path $folder 'result.json') -Raw | ConvertFrom-Json
 $metadata = Get-Content -LiteralPath (Join-Path $folder 'metadata.json') -Raw | ConvertFrom-Json
 $testedConfig = Get-Content -LiteralPath (Join-Path $folder 'config.json') -Raw | ConvertFrom-Json
 if ($result.status -ne 'platform_reached' -or $metadata.emulator_sha256 -ine $evidence.emulator_sha256) {
  throw "Candidate route does not match: $run"
 }
 if ($testedConfig.GPU.readbacks_mode -ne 1 -or
     $testedConfig.Vulkan.pipeline_cache_enabled -ne $evidence.pipeline_cache_enabled) {
  throw "Route used a different GPU memory/cache profile: $run"
 }
}
New-Item -ItemType Directory -Path $destination -Force | Out-Null
$backup = Join-Path $destination ('launcher-backups/' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
New-Item -ItemType Directory -Path $backup | Out-Null
function BatchPath([string]$path) {
 if ($path -match '["\r\n]') { throw 'Unsupported launcher path.' }
 return '"' + $path.Replace('%','%%') + '"'
}
$command = (BatchPath $Python) + ' ' + (BatchPath $launcher) + ' --development-root ' +
 (BatchPath $runtime) + ' --game ' + (BatchPath $Game) + ' --renderer-sync pass --real-occlusion'
foreach ($entry in @(
 @{Name='Launch-Here-They-Lie-No-Vignette.cmd'; Mode='preview'; Tv=$false},
 @{Name='Play-Here-They-Lie-SteamVR-No-Vignette.cmd'; Mode='quest'; Tv=$false},
 @{Name='Launch-Here-They-Lie-With-TV.cmd'; Mode='preview'; Tv=$true},
 @{Name='Play-Here-They-Lie-SteamVR-With-TV.cmd'; Mode='quest'; Tv=$true}
)) {
 $path = Join-Path $destination $entry.Name
 if (Test-Path -LiteralPath $path) { Copy-Item -LiteralPath $path -Destination $backup }
 $lines = @('@echo off','setlocal DisableDelayedExpansion')
 if ($entry.Mode -eq 'quest') {
  $lines += 'set "VR_PATHREG_OVERRIDE="'
  $lines += 'set "XR_RUNTIME_JSON=C:\Program Files (x86)\Steam\steamapps\common\SteamVR\steamxr_win64.json"'
  $lines += 'if not exist "%XR_RUNTIME_JSON%" (echo SteamVR runtime was not found. & pause & exit /b 1)'
 }
 $lines += $command + ' --mode ' + $entry.Mode
 if ($entry.Tv) { $lines[-1] += ' --tv-preview' }
 $lines += @('if errorlevel 1 pause','endlocal')
 [IO.File]::WriteAllLines($path, $lines, [Text.UTF8Encoding]::new($false))
}
Write-Output "Launchers now use $runtime. Previous launchers are in $backup."
Write-Output 'The optional TV window stays off. Physical headset comfort and sustained 60 FPS are not certified by route completion.'
