# 喜马拉雅 XM 解密工具

把喜马拉雅下载下来的 `.xm` 文件解密成常见音频格式。程序在本地处理文件，解密后会尽量保留标题、专辑和艺术家等信息，输出格式支持 `m4a`、`mp3`、`flac` 和 `wav`。

当前版本：**v1.0.5**

> 请只处理你有权使用的音频，并遵守喜马拉雅的服务条款和当地法律。

## 下载

去 [Releases](https://github.com/a176073240-cmd/Ximalaya-Decrypt-Enhance/releases) 下载最新版本。

目前发布的是源码压缩包 `Ximalaya-Decrypt-v1.0.5.zip`，解压后可以看到：

```text
main.py
rename.py
xm_encryptor.wasm
README.md
```

暂时没有打包好的 `.exe`。直接运行源码需要安装 Python 和项目依赖；`xm_encryptor.wasm` 也要和 `main.py` 放在一起，不能漏掉。

## 运行源码

目前建议在 64 位 Windows、Python 3.10 环境下运行。打开 PowerShell，进入项目目录后执行：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install mutagen pycryptodome wasmer==1.1.0 wasmer_compiler_cranelift==1.1.0 python-magic-bin
python main.py
```

如果 PowerShell 不允许执行虚拟环境脚本，可以直接调用虚拟环境里的 Python：

```powershell
.\.venv\Scripts\python.exe main.py
```

## 解密文件

启动 `main.py` 后，按菜单提示操作：

1. 选“解密单个文件”，处理一个 `.xm` 文件；或者选“批量解密文件”，处理一个文件夹里的文件。
2. 批量模式只看所选文件夹的第一层，不会继续扫描子文件夹。
3. 程序会问你要不要在文件名前加集数，例如 `0204 - 标题.m4a`。集数取自 XM 文件的元数据。
4. 再选择输出目录。不指定时，文件会放在程序目录下的 `output` 文件夹。

不同专辑会分开放置，目录大致如下：

```text
output/
└─ 专辑名称/
   ├─ 0204 - 第204集.m4a
   └─ 第205集.m4a
```

输出目录里如果已经有同名文件，程序会自动在文件名后加 `(1)`、`(2)`，不会把原文件覆盖掉。遇到空文件、损坏文件或暂时识别不了的音频时，该文件会被跳过，任务结束后可以在失败清单里查看原因，其他文件不受影响。

## 整理文件名

`rename.py` 可以把已经解密好的音频重新编号，支持 `.mp3`、`.m4a`、`.flac` 和 `.wav`：

```powershell
python rename.py
```

选择音频文件夹后，它会尝试把文件名整理成这样：

```text
[0001] 标题.m4a
[0002] 标题.m4a
```

程序会去掉原有的 `[0001]` 前缀，并把文件名里找到的第一段数字当作集数。如果标题本身带数字，改名后请顺手检查一下。遇到重名文件时不会强行覆盖，而是放进失败清单。这个脚本同样只处理当前文件夹，不会递归子目录；批量改名前建议先备份。

## v1.0.5 更新

- 修复部分解密数据末尾字节丢失的问题。
- 改进加密数据长度检查，文件不完整时会给出提示。
- XM 文件缺少必要信息时，报错内容更容易看懂。
- 处理非法文件名、Windows 保留名称和危险路径。
- 输出文件重名时不再静默覆盖。
- 修复批量重命名时的文件名冲突和交换问题。

## 常见问题

### `ModuleNotFoundError`

一般是依赖装到了另一个 Python 环境。请在运行程序的同一个 PowerShell 窗口里重新安装：

```powershell
python -m pip install mutagen pycryptodome wasmer==1.1.0 wasmer_compiler_cranelift==1.1.0 python-magic-bin
```

### 找不到 `xm_encryptor.wasm`

确认 `xm_encryptor.wasm` 和 `main.py` 在同一个目录，不要只复制 Python 文件。

### `unexpected format`

通常是 `.xm` 文件没有下载完整、文件已经损坏，或者当前格式还不支持。重新下载文件后再试试。

### 文件选择窗口没有弹出

工具依赖 Windows 的图形界面选择文件。请在正常的 Windows 桌面环境中运行，不要在没有图形界面的远程终端里运行。

## 鸣谢

这个项目是在 [sld272/Ximalaya-XM-Decrypt](https://github.com/sld272/Ximalaya-XM-Decrypt) 的基础上继续维护的，感谢原作者提供 `xm_encryptor.wasm` 和最初的 Python 实现。

遇到问题时，欢迎附上错误信息、文件大小和音频格式。请不要上传带有个人信息或版权受限的音频文件。
