param([string]$ToolsRoot = "$([Environment]::GetFolderPath('MyDocuments'))/Codex/DevTools/htl")
$ErrorActionPreference = 'Stop'
$lock = Get-Content "$PSScriptRoot/../toolchain.lock.json" -Raw | ConvertFrom-Json
New-Item -ItemType Directory -Force "$ToolsRoot/downloads" | Out-Null
foreach ($item in $lock.archives) {
 $archive = Join-Path "$ToolsRoot/downloads" $item.name
 if (-not (Test-Path $archive)) { Invoke-WebRequest $item.url -OutFile $archive }
 if ((Get-FileHash $archive -Algorithm SHA256).Hash.ToLowerInvariant() -ne $item.sha256) { throw "Download hash mismatch: $($item.name)" }
 $destination = if ($item.folder -eq 'llvm') { $ToolsRoot } else { Join-Path $ToolsRoot $item.folder }
 New-Item -ItemType Directory -Force $destination | Out-Null
 if ($item.name.EndsWith('.zip')) { Expand-Archive -LiteralPath $archive -DestinationPath $destination -Force }
 else { & tar.exe -xf $archive -C $destination; if ($LASTEXITCODE -ne 0) { throw "Unpack failed: $($item.name)" } }
}
$xwin = "$ToolsRoot/xwin/xwin-0.10.0-x86_64-pc-windows-msvc/xwin.exe"
& $xwin --accept-license --cache-dir "$ToolsRoot/xwin-cache" --http-retry 3 --timeout 120 --sdk-version $lock.sdk_version --crt-version $lock.crt_directory_version splat --disable-symlinks --use-winsysroot-style --preserve-ms-arch-notation --output "$ToolsRoot/winsysroot"
if ($LASTEXITCODE -ne 0) { throw 'Windows SDK preparation failed' }
