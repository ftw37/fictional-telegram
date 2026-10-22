param([string]$ToolsRoot = "$([Environment]::GetFolderPath('MyDocuments'))/Codex/DevTools/htl")
$llvm = Join-Path $ToolsRoot 'clang+llvm-20.1.8-x86_64-pc-windows-msvc/bin'
$cmake = Join-Path $ToolsRoot 'cmake/cmake-4.4.4-windows-x86_64/bin'
$sdkRoot = Join-Path $ToolsRoot 'winsysroot'
$env:PATH = "$llvm;$cmake;$ToolsRoot/ninja;$ToolsRoot/git/cmd;$env:PATH"
foreach ($tool in 'git','cmake','ninja','clang-cl','lld-link','llvm-rc') {
 if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) { throw "Missing build tool: $tool" }
}
if (-not (Test-Path "$sdkRoot/Windows Kits")) { throw "Windows SDK is not prepared in $sdkRoot" }
$crt = Get-ChildItem "$sdkRoot/VC/Tools/MSVC" -Directory | Sort-Object Name -Descending | Select-Object -First 1
$sdk = Get-ChildItem "$sdkRoot/Windows Kits/10/Include" -Directory | Sort-Object Name -Descending | Select-Object -First 1
$env:INCLUDE = "$($crt.FullName)/include;$($sdk.FullName)/ucrt;$($sdk.FullName)/um;$($sdk.FullName)/shared;$($sdk.FullName)/winrt;$($sdk.FullName)/cppwinrt"
$env:LIB = "$($crt.FullName)/lib/x64;$sdkRoot/Windows Kits/10/Lib/$($sdk.Name)/um/x64;$sdkRoot/Windows Kits/10/Lib/$($sdk.Name)/ucrt/x64"
