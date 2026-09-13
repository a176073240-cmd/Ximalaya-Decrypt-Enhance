$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $projectRoot

python -m pip install --upgrade pyinstaller mutagen pycryptodome wasmtime python-magic-bin

$wasmtimeDll = python -c "import pathlib, wasmtime; print(pathlib.Path(wasmtime.__file__).parent / 'win32-x86_64' / '_wasmtime.dll')"
$wasmtimeDll = $wasmtimeDll.Trim()
if (-not (Test-Path -LiteralPath $wasmtimeDll)) {
    throw "找不到 Wasmtime DLL: $wasmtimeDll"
}

pyinstaller --noconfirm --clean --onefile --console `
    --name Ximalaya-Decrypt `
    --add-data "xm_encryptor.wasm;." `
    --add-binary "$wasmtimeDll;wasmtime/win32-x86_64" `
    main.py

pyinstaller --noconfirm --clean --onefile --console `
    --name Ximalaya-Rename `
    rename.py

Write-Host "构建完成：dist\Ximalaya-Decrypt.exe 和 dist\Ximalaya-Rename.exe"
