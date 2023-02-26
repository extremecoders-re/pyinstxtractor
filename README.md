# PyInstaller Extractor

PyInstaller Extractor is a Python script to extract the contents of a PyInstaller generated executable file.

The header of the pyc files are automatically fixed so that a Python bytecode decompiler will recognize it. The script can run on both Python 2.x and 3.x. PyInstaller versions 2.0, 2.1, 3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 4.0, 4.1, 4.2, 4.3, 4.4, 4.5, 4.5.1, 4.6, 4.7, 4.8, 4.9, 4.10, 5.0, 5.0.1, 5.1, 5.2, 5.3, 5.4, 5.4.1, 5.5, 5.6, 5.6.1, 5.6.2, 5.7.0, 5.8.0 are [tested](https://github.com/pyinstxtractor/pyinstxtractor-test-binaries) & supported. Probably will work with other versions too.

This project was originally hosted on [SourceForge](https://sourceforge.net/projects/pyinstallerextractor/).

## Usage

The script can be run by passing the name of the exe as an argument.

```
$ python pyinstxtractor.py <filename>
X:\>python pyinstxtractor.py <filename>
```

It is recommended to run the script in the same version of Python which was used to generate the executable. This is to prevent unmarshalling errors(if any) while extracting the PYZ archive.

## Example

```
X:\> python pyinstxtractor.py test.exe
[+] Processing dist\test.exe
[+] Pyinstaller version: 2.1+
[+] Python version: 36
[+] Length of package: 5612452 bytes
[+] Found 59 files in CArchive
[+] Beginning extraction...please standby
[+] Possible entry point: pyiboot01_bootstrap.pyc
[+] Possible entry point: test.pyc
[+] Found 133 files in PYZ archive
[+] Successfully extracted pyinstaller archive: dist\test.exe

You can now use a python decompiler on the pyc files within the extracted directory
```

After extracting the pyc's you can use a Python decompiler like [Uncompyle6](https://github.com/rocky/python-uncompyle6/) and [Decompyle++](https://github.com/zrax/pycdc).

```
X:\> uncompyle6.exe test.exe_extracted\test.pyc
X:\> uncompyle6.exe test.exe_extracted\PYZ-00.pyz_extracted\__future__.pyc
```
## Extracting Linux ELF binaries

Pyinstxtractor can natively extract Linux ELF binaries without requiring other tools.

For other questions and information, please see the [Wiki](https://github.com/extremecoders-re/pyinstxtractor/wiki/Extracting-Linux-ELF-binaries) and the [FAQ](https://github.com/extremecoders-re/pyinstxtractor/wiki/Frequently-Asked-Questions)

## See also

- [pyinstxtractor-ng](https://github.com/pyinstxtractor/pyinstxtractor-ng): 
A standalone binary version of pyinstxtractor. This tool doesn't require Python to run and can extract all supported versions of PyInstaller. It also supports encrypted pyinstaller executables.
- [pyinstxtractor-web](https://github.com/pyinstxtractor/pyinstxtractor-go): pyinstxtractor running in the web browser, powered by Go & GopherJS.

## License

GNU General Public License v3.0
