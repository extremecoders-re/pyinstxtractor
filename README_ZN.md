## PyInstaller Extractor（PyInstaller 解包工具）

**PyInstaller Extractor** 是一个用于提取由 PyInstaller 打包生成的可执行文件（`.exe`）内容的 Python 脚本。

该脚本会自动修复 `.pyc` 文件的头部信息，使得 Python 字节码反编译器能够正确识别。脚本兼容 Python 2.x 和 3.x 版本。

支持的 PyInstaller 版本包括：

> 2.0、2.1、3.0、3.1、3.2、3.3、3.4、3.5、3.6、4.0、4.1、4.2、4.3、4.4、4.5、4.5.1、4.6、4.7、4.8、4.9、4.10、5.0、5.0.1、5.1、5.2、5.3、5.4、5.4.1、5.5、5.6、5.6.1、5.6.2、5.7.0、5.8.0、5.9.0、5.10.0、5.10.1、5.11.0、5.12.0、5.13.0、5.13.1、5.13.2、6.0.0、6.1.0、6.2.0、6.3.0、6.4.0、6.5.0、6.6.0、6.7.0、6.8.0、6.9.0、6.10.0、6.11.0、6.11.1、6.12.0、6.13.0、6.14.0

其他版本可能也可以正常工作。

> 该项目最初托管在 SourceForge。

------

## 使用方法

运行该脚本时，将目标 `.exe` 文件作为参数传入：

```bash
$ python pyinstxtractor.py <文件名>
```

例如：

```bash
X:\> python pyinstxtractor.py test.exe
```

**建议使用与该 `.exe` 文件打包时相同版本的 Python 运行此脚本**，以避免在解包 PYZ 文件时出现反序列化（unmarshalling）错误。

------

## 示例输出

```text
X:\> python pyinstxtractor.py test.exe
[+] 正在处理 dist\test.exe
[+] PyInstaller 版本: 2.1+
[+] Python 版本: 3.6
[+] 包大小: 5612452 字节
[+] CArchive 中找到 59 个文件
[+] 正在开始提取，请稍候...
[+] 可能的入口文件: pyiboot01_bootstrap.pyc
[+] 可能的入口文件: test.pyc
[+] 在 PYZ 压缩包中找到 133 个文件
[+] 成功提取 PyInstaller 包: dist\test.exe
```

------

## 提取后反编译

提取完成后，你可以使用 Python 反编译工具（如 `uncompyle6` 或 `decompyle++`）对 `.pyc` 文件进行反编译：

```bash
X:\> uncompyle6.exe test.exe_extracted\test.pyc
X:\> uncompyle6.exe test.exe_extracted\PYZ-00.pyz_extracted\__future__.pyc
```

------

## Linux ELF 文件的提取

**pyinstxtractor** 原生支持提取 Linux ELF 格式的二进制文件，**不需要其他工具**辅助。

------

## 其他相关工具

- **pyinstxtractor-ng**：pyinstxtractor 的独立可执行版本，不需要 Python 环境即可运行，支持所有受支持的 PyInstaller 版本，同时支持加密的 PyInstaller 可执行文件。
- **pyinstxtractor-web**：运行在浏览器中的 pyinstxtractor，基于 Go 和 GopherJS 实现。

------

## 许可证

本项目遵循 **GNU 通用公共许可证 v3.0**（GPLv3）。
