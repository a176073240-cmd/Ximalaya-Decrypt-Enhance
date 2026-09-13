# 喜马拉雅 XM 解密工具

这是一个在电脑本地运行的 `.xm` 音频解密工具，可以把解密后的音频保存为 `m4a`、`mp3`、`flac` 或 `wav`。音频里的标题、专辑和艺术家信息也会一并写入文件。

当前版本：**v1.0.5**

请只处理你有权使用的音频，并遵守喜马拉雅的服务条款和当地法律。

## 下载

到 [Releases](https://github.com/a176073240-cmd/Ximalaya-Decrypt-Enhance/releases) 页面下载最新版本。

目前 Release 里提供的是源码压缩包 `Ximalaya-Decrypt-v1.0.5.zip`，里面有：

```text
main.py
rename.py
xm_encryptor.wasm
README.md
```

仓库暂时没有提供预编译的 `.exe`。如果你直接运行源码，需要安装 Python 和下面列出的依赖。`xm_encryptor.wasm` 必须和 `main.py` 放在同一个目录里。

## 直接运行源码

建议使用 64 位 Windows 和 Python 3.10。先打开 PowerShell，在项目目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install mutagen pycryptodome wasmer==1.1.0 wasmer_compiler_cranelift==1.1.0 python-magic-bin
```

然后启动程序：

```powershell
python main.py
```

如果虚拟环境脚本被 PowerShell 拦截，也可以直接运行：

```powershell
.\.venv\Scripts\python.exe main.py
```

## 怎么用

运行 `main.py` 后，菜单里有三个选项：

1. **解密单个文件**：选择一个 `.xm` 文件。
2. **批量解密文件**：选择一个文件夹，程序只处理这个文件夹第一层的 `.xm` 文件，不会进入子文件夹。
3. **退出**。

选择文件后，程序会询问两个问题：

- 是否在文件名前加集数，例如 `0204 - 标题.m4a`。集数来自 XM 文件自身的元数据。
- 是否指定输出目录。不指定时，文件会保存到程序当前工作目录下的 `output` 文件夹。

每张专辑会单独放在一个文件夹中，例如：

```text
output/
└─ 专辑名称/
   ├─ 0204 - 第204集.m4a
   └─ 第205集.m4a
```

如果输出目录里已经有同名文件，程序会在新文件名后加上 `(1)`、`(2)`，不会直接覆盖原文件。

遇到空文件、损坏文件或无法识别的音频时，程序会跳过该文件，任务结束后在失败清单里显示原因，其他文件仍会继续处理。

## 文件名整理工具

`rename.py` 用来整理已经解密好的音频文件名。它支持 `.mp3`、`.m4a`、`.flac` 和 `.wav`。

```powershell
python rename.py
```

运行后选择音频文件夹，工具会把文件名整理成类似下面的格式：

```text
[0001] 标题.m4a
[0002] 标题.m4a
```

它会尝试删除原来的 `[0001]` 前缀，并把文件名中找到的第一段数字当作集数。标题中本来就有数字时，建议改名后检查一下结果。目标名称重复的文件不会强行覆盖，会列在失败清单中。

这个工具同样只处理所选文件夹的第一层，不会递归子目录。批量改名之前，最好先备份文件名或整个文件夹。

## v1.0.5 更新内容

- 修复部分解密数据末尾字节丢失的问题。
- 改进加密数据长度处理，遇到不完整文件时给出提示。
- XM 文件缺少必要信息时，显示更明确的错误。
- 处理非法文件名、Windows 保留名称和危险路径。
- 输出文件重名时不再静默覆盖。
- 修复批量重命名时的文件名冲突和交换问题。

## 常见问题

### 提示 `ModuleNotFoundError`

通常是依赖没有装到当前使用的 Python 里。请在运行程序的同一个终端重新执行：

```powershell
python -m pip install mutagen pycryptodome wasmer==1.1.0 wasmer_compiler_cranelift==1.1.0 python-magic-bin
```

### 提示找不到 `xm_encryptor.wasm`

确认这个文件和 `main.py` 在同一目录，不要只复制 Python 脚本。

### 提示 `unexpected format`

程序没有识别出解密后的音频格式。一般是源 `.xm` 文件下载不完整、文件已损坏，或格式暂不支持。可以重新下载后再试。

### 文件选择窗口没有打开

程序使用 Windows 的图形界面选择文件和文件夹，请在正常的 Windows 桌面环境运行。

## 鸣谢

本项目基于 [sld272/Ximalaya-XM-Decrypt](https://github.com/sld272/Ximalaya-XM-Decrypt) 继续维护。感谢原作者提供 `xm_encryptor.wasm` 和基础 Python 实现。

反馈问题时，请附上错误信息、文件大小和音频格式等信息。请不要上传包含个人信息或版权受限的音频文件。
