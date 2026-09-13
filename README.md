# 喜马拉雅 XM 解密工具

一个在本地运行的喜马拉雅 `.xm` 音频解密工具。项目使用 WebAssembly 解密核心完成格式转换，并保留原始音频流和主要元数据。

当前版本：**v1.0.5**

> 仅处理你有权访问和转换的音频文件。请遵守相关服务条款、版权和当地法律。

## 功能

- 单个文件解密：通过文件选择窗口选择一个 `.xm` 文件。
- 批量解密：选择文件夹后，处理该文件夹下的 `.xm` 文件（不递归扫描子目录）。
- 自动识别输出格式：支持 `m4a`、`mp3`、`flac` 和 `wav`。
- 自动写入标题、专辑和艺术家标签。
- 完整性检查：空文件、缺少 XM 元数据、无法识别的音频和明显不完整的文件会进入失败清单，不会中断整个批处理。
- 安全文件名：清理 Windows 非法字符、保留设备名和危险路径名称。
- 重名保护：目标文件已存在时自动生成 `(1)`、`(2)` 等后缀，避免静默覆盖。
- 附带 `rename.py`：按文件名中的集数统一补零排序。

## 获取程序

前往 [Releases](https://github.com/a176073240-cmd/Ximalaya-Decrypt-Enhance/releases) 下载版本附件。

当前 `v1.0.5` Release 提供源码运行包 `Ximalaya-Decrypt-v1.0.5.zip`，其中包含：

```text
main.py
rename.py
xm_encryptor.wasm
README.md
```

本仓库当前没有提交预编译 `.exe`。如果需要直接双击运行的 Windows 程序，请按项目代码自行构建或使用可信的构建产物；无论使用源码还是打包程序，`xm_encryptor.wasm` 都必须与入口程序放在同一目录。

## 源码运行

建议使用 64 位 Windows 和 Python 3.10。创建虚拟环境后安装依赖：

```bash
python -m venv .venv
```

Windows PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install mutagen pycryptodome wasmer==1.1.0 wasmer_compiler_cranelift==1.1.0 python-magic-bin
```

启动主程序：

```powershell
python main.py
```

如果 PowerShell 阻止虚拟环境脚本，可以直接使用虚拟环境中的解释器：

```powershell
.\.venv\Scripts\python.exe main.py
```

## 解密流程

1. 运行 `main.py`。
2. 选择“解密单个文件”或“批量解密文件”。
3. 选择是否使用 XM 文件内的集数生成前缀，例如 `0204 - 标题.m4a`。
4. 选择输出目录；不指定时，输出到当前工作目录下的 `output` 文件夹。
5. 等待任务报告。失败文件会列出文件名和原因，可回到来源客户端重新下载后再处理。

输出目录结构示例：

```text
output/
└─ 专辑名称/
   ├─ 0204 - 第204集.m4a
   └─ 第205集.m4a
```

批量模式只读取所选目录的第一层，不会自动处理子目录。需要处理子目录时，请分别选择目录，或在外部整理文件后再运行。

## 文件名排序工具

`rename.py` 是独立的 GUI 小工具，支持 `.mp3`、`.m4a`、`.flac` 和 `.wav`。

```powershell
python rename.py
```

选择音频文件夹后，工具会：

- 清理已有的 `[0001]` 类前缀；
- 查找文件名中的第一段数字作为集数；
- 生成类似 `[0001] 标题.m4a` 的名称；
- 检测重复目标名称，冲突文件会列入失败清单；
- 只处理所选文件夹的第一层，不递归子目录。

建议在批量改名之前备份文件名列表。对于标题本身含有多个数字的文件，工具无法理解语义，可能需要手动复核结果。

## v1.0.5 更新

- 修复可打印数据处理导致的末尾字节丢失。
- 改进 AES 解密数据长度处理，兼容非完整块的旧 XM 变体。
- XM 元数据缺失时给出明确错误，而不是直接抛出难以定位的键错误。
- 清理非法路径、Windows 保留设备名和空文件名。
- 防止输出文件被静默覆盖。
- 修复批量重命名时的目标冲突和文件交换问题。

## 常见问题

### `ModuleNotFoundError`

确认当前终端使用的是安装依赖的 Python，并重新执行安装命令：

```powershell
python -m pip install mutagen pycryptodome wasmer==1.1.0 wasmer_compiler_cranelift==1.1.0 python-magic-bin
```

### 找不到 `xm_encryptor.wasm`

将 `xm_encryptor.wasm` 放到 `main.py` 同一目录。不要只复制 Python 文件运行。

### `unexpected format`

解密后的音频头无法被系统识别，常见原因是 XM 文件损坏、下载不完整或格式不受支持。重新下载源文件后再试。

### tkinter 无法打开窗口

主程序和重命名工具都需要桌面环境。请在 Windows 桌面终端运行，不要在无图形界面的远程或服务器环境中启动。

## 鸣谢

本项目基于 [sld272/Ximalaya-XM-Decrypt](https://github.com/sld272/Ximalaya-XM-Decrypt) 继续维护。感谢原作者逆向并提供 WebAssembly 解密核心 `xm_encryptor.wasm` 及基础 Python 实现。

如发现无法处理的文件，请提交 Issue，并尽量提供错误信息、文件大小和格式信息。不要上传包含个人信息或版权受限的音频文件。
