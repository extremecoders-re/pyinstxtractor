"""
PyInstaller Extractor v2.0 (Supports pyinstaller 6.11.1, 6.11.0, 6.10.0, 6.9.0, 6.8.0, 6.7.0, 6.6.0, 6.5.0, 6.4.0, 6.3.0, 6.2.0, 6.1.0, 6.0.0, 5.13.2, 5.13.1, 5.13.0, 5.12.0, 5.11.0, 5.10.1, 5.10.0, 5.9.0, 5.8.0, 5.7.0, 5.6.2, 5.6.1, 5.6, 5.5, 5.4.1, 5.4, 5.3, 5.2, 5.1, 5.0.1, 5.0, 4.10, 4.9, 4.8, 4.7, 4.6, 4.5.1, 4.5, 4.4, 4.3, 4.2, 4.1, 4.0, 3.6, 3.5, 3.4, 3.3, 3.2, 3.1, 3.0, 2.1, 2.0)
Author : Extreme Coders
E-mail : extremecoders(at)hotmail(dot)com
Web    : https://0xec.blogspot.com
Date   : 26-March-2020
Url    : https://github.com/extremecoders-re/pyinstxtractor

For any suggestions, leave a comment on
https://forum.tuts4you.com/topic/34455-pyinstaller-extractor/

This script extracts a pyinstaller generated executable file.
Pyinstaller installation is not needed. The script has it all.

For best results, it is recommended to run this script in the
same version of python as was used to create the executable.
This is just to prevent unmarshalling errors(if any) while
extracting the PYZ archive.

Usage : Just copy this script to the directory where your exe resides
        and run the script with the exe file name as a parameter

C:\\path\\to\\exe\\>python pyinstxtractor.py <filename>
$ /path/to/exe/python pyinstxtractor.py <filename>

Licensed under GNU General Public License (GPL) v3.
You are free to modify this source.

CHANGELOG
================================================

Version 1.1 (Jan 28, 2014)
-------------------------------------------------
- First Release
- Supports only pyinstaller 2.0

Version 1.2 (Sept 12, 2015)
-------------------------------------------------
- Added support for pyinstaller 2.1 and 3.0 dev
- Cleaned up code
- Script is now more verbose
- Executable extracted within a dedicated sub-directory

(Support for pyinstaller 3.0 dev is experimental)

Version 1.3 (Dec 12, 2015)
-------------------------------------------------
- Added support for pyinstaller 3.0 final
- Script is compatible with both python 2.x & 3.x (Thanks to Moritz Kroll @ Avira Operations GmbH & Co. KG)

Version 1.4 (Jan 19, 2016)
-------------------------------------------------
- Fixed a bug when writing pyc files >= version 3.3 (Thanks to Daniello Alto: https://github.com/Djamana)

Version 1.5 (March 1, 2016)
-------------------------------------------------
- Added support for pyinstaller 3.1 (Thanks to Berwyn Hoyt for reporting)

Version 1.6 (Sept 5, 2016)
-------------------------------------------------
- Added support for pyinstaller 3.2
- Extractor will use a random name while extracting unnamed files.
- For encrypted pyz archives it will dump the contents as is. Previously, the tool would fail.

Version 1.7 (March 13, 2017)
-------------------------------------------------
- Made the script compatible with python 2.6 (Thanks to Ross for reporting)

Version 1.8 (April 28, 2017)
-------------------------------------------------
- Support for sub-directories in .pyz files (Thanks to Moritz Kroll @ Avira Operations GmbH & Co. KG)

Version 1.9 (November 29, 2017)
-------------------------------------------------
- Added support for pyinstaller 3.3
- Display the scripts which are run at entry (Thanks to Michael Gillespie @ malwarehunterteam for the feature request)

Version 2.0 (March 26, 2020)
-------------------------------------------------
- Project migrated to github
- Supports pyinstaller 3.6
- Added support for Python 3.7, 3.8
- The header of all extracted pyc's are now automatically fixed
"""

import logging
import marshal
import os
import struct
import sys
import zlib
from contextlib import suppress
from uuid import uuid4 as uniquename

log = logging.getLogger()


class CTOCEntry:
    def __init__(self, position, cmprsdDataSize, uncmprsdDataSize, cmprsFlag, typeCmprsData, name):
        self.position = position
        self.cmprsdDataSize = cmprsdDataSize
        self.uncmprsdDataSize = uncmprsdDataSize
        self.cmprsFlag = cmprsFlag
        self.typeCmprsData = typeCmprsData
        self.name = name


class PyInstArchive:
    PYINST20_COOKIE_SIZE = 24  # For pyinstaller 2.0
    PYINST21_COOKIE_SIZE = 24 + 64  # For pyinstaller 2.1+
    MAGIC = b"MEI\014\013\012\013\016"  # Magic number which identifies pyinstaller

    def __init__(self, kwargs):
        self.filePath = kwargs["file"]
        self.destination_folder = kwargs["destination_folder"]
        self.only_entrypoints = kwargs["entry_points"]
        self.pycMagic = b"\0" * 4
        self.barePycList = []  # List of pyc's whose headers have to be fixed

    def open(self):
        try:
            self.fPtr = open(self.filePath, "rb")
            self.fileSize = os.stat(self.filePath).st_size
        except Exception as e:
            log.error("[!] Could not open: %s. Error: %s", self.filePath, str(e))
            return False
        return True

    def close(self):
        with suppress(Exception):
            self.fPtr.close()

    def checkFile(self):
        log.debug("[+] Processing %s", self.filePath)
        searchChunkSize = 8192
        endPos = self.fileSize
        self.cookiePos = -1

        if endPos < len(self.MAGIC):
            log.error("[!] File is too short or truncated")
            return False

        while True:
            startPos = endPos - searchChunkSize if endPos >= searchChunkSize else 0
            chunkSize = endPos - startPos
            if chunkSize < len(self.MAGIC):
                break

            self.fPtr.seek(startPos, os.SEEK_SET)
            data = self.fPtr.read(chunkSize)
            offs = data.rfind(self.MAGIC)
            if offs != -1:
                self.cookiePos = startPos + offs
                break

            endPos = startPos + len(self.MAGIC) - 1
            if startPos == 0:
                break

        if self.cookiePos == -1:
            log.error("[!] Missing cookie, unsupported pyinstaller version or not a pyinstaller archive")
            return False

        self.fPtr.seek(self.cookiePos + self.PYINST20_COOKIE_SIZE, os.SEEK_SET)
        if b"python" in self.fPtr.read(64).lower():
            log.debug("[+] Pyinstaller version: 2.1+")
            self.pyinstVer = 21  # pyinstaller 2.1+
        else:
            self.pyinstVer = 20  # pyinstaller 2.0
            log.debug("[+] Pyinstaller version: 2.0")
        return True

    def getCArchiveInfo(self):
        try:
            if self.pyinstVer == 20:
                self.fPtr.seek(self.cookiePos, os.SEEK_SET)
                # Read CArchive cookie
                (magic, lengthofPackage, toc, tocLen, pyver) = struct.unpack("!8siiii", self.fPtr.read(self.PYINST20_COOKIE_SIZE))
            elif self.pyinstVer == 21:
                self.fPtr.seek(self.cookiePos, os.SEEK_SET)
                # Read CArchive cookie
                (magic, lengthofPackage, toc, tocLen, pyver, pylibname) = struct.unpack(
                    "!8sIIii64s", self.fPtr.read(self.PYINST21_COOKIE_SIZE)
                )
        except Exception as e:
            log.error("[!] The file is not a pyinstaller archive: %s", str(e))
            return False

        self.pymaj, self.pymin = (pyver // 100, pyver % 100) if pyver >= 100 else (pyver // 10, pyver % 10)
        log.debug("[+] Python version: %d.%d", self.pymaj, self.pymin)

        # Additional data after the cookie
        tailBytes = (
            self.fileSize - self.cookiePos - (self.PYINST20_COOKIE_SIZE if self.pyinstVer == 20 else self.PYINST21_COOKIE_SIZE)
        )

        # Overlay is the data appended at the end of the PE
        self.overlaySize = lengthofPackage + tailBytes
        self.overlayPos = self.fileSize - self.overlaySize
        self.tableOfContentsPos = self.overlayPos + toc
        self.tableOfContentsSize = tocLen

        log.debug("[+] Length of package: %d bytes", lengthofPackage)
        return True

    def parseTOC(self):
        # Go to the table of contents
        self.fPtr.seek(self.tableOfContentsPos, os.SEEK_SET)

        self.tocList = []
        parsedLen = 0

        # Parse table of contents
        while parsedLen < self.tableOfContentsSize:
            (entrySize,) = struct.unpack("!i", self.fPtr.read(4))
            nameLen = struct.calcsize("!iIIIBc")

            (entryPos, cmprsdDataSize, uncmprsdDataSize, cmprsFlag, typeCmprsData, name) = struct.unpack(
                "!IIIBc{0}s".format(entrySize - nameLen), self.fPtr.read(entrySize - 4)
            )

            try:
                name = name.decode("utf-8").rstrip("\0")
            except UnicodeDecodeError:
                newName = str(uniquename())
                log.warning("[!] File name %s contains invalid bytes. Using random name %s", name, newName)
                name = newName

            # Prevent writing outside the extraction directory
            if name.startswith("/"):
                name = name.lstrip("/")

            if len(name) == 0:
                name = str(uniquename())
                log.warning("[!] Found an unamed file in CArchive. Using random name %s", name)

            self.tocList.append(
                CTOCEntry(self.overlayPos + entryPos, cmprsdDataSize, uncmprsdDataSize, cmprsFlag, typeCmprsData, name)
            )

            parsedLen += entrySize
        log.info("[+] Found %d files in CArchive", len(self.tocList))

    def _writeRawData(self, filepath, data):
        nm = filepath.replace("\\", os.path.sep).replace("/", os.path.sep).replace("..", "__")
        nmDir = os.path.dirname(nm)
        if nmDir != "" and not os.path.exists(nmDir):  # Check if path exists, create if not
            os.makedirs(nmDir)

        with open(nm, "wb") as f:
            f.write(data)

    def extractFiles(self):
        log.debug("[+] Beginning extraction...please standby")
        # extractionDir = os.path.join(os.getcwd(), os.path.basename(self.filePath) + "_extracted")
        extractionDir = self.destination_folder
        if not os.path.exists(extractionDir):
            os.mkdir(extractionDir)

        # os.chdir(extractionDir)

        for entry in self.tocList:
            destination_entry = os.path.join(self.destination_folder, entry.name)
            self.fPtr.seek(entry.position, os.SEEK_SET)
            data = self.fPtr.read(entry.cmprsdDataSize)

            if entry.cmprsFlag == 1:
                try:
                    data = zlib.decompress(data)
                except zlib.error:
                    log.error("[!] Failed to decompress %s", entry.name)
                    continue
                # Malware may tamper with the uncompressed size
                # Comment out the assertion in such a case
                assert len(data) == entry.uncmprsdDataSize  # Sanity Check

            if entry.typeCmprsData in (b"d", b"o"):
                # d -> ARCHIVE_ITEM_DEPENDENCY
                # o -> ARCHIVE_ITEM_RUNTIME_OPTION
                # These are runtime options, not files
                continue

            basePath = os.path.dirname(entry.name)
            if basePath != "":
                # Check if path exists, create if not
                if not os.path.exists(basePath):
                    os.makedirs(basePath)

            if entry.typeCmprsData == b"s":
                # s -> ARCHIVE_ITEM_PYSOURCE
                # Entry point are expected to be python scripts
                log.info("[+] Possible entry point: %s.pyc", entry.name)

                if self.pycMagic == b"\0" * 4:
                    # if we don't have the pyc header yet, fix them in a later pass
                    self.barePycList.append(destination_entry + ".pyc")
                self._writePyc(destination_entry + ".pyc", data)

            elif entry.typeCmprsData == (b"M", b"m") and not self.only_entrypoints:
                # M -> ARCHIVE_ITEM_PYPACKAGE
                # m -> ARCHIVE_ITEM_PYMODULE
                # packages and modules are pyc files with their header intact

                # From PyInstaller 5.3 and above pyc headers are no longer stored
                # https://github.com/pyinstaller/pyinstaller/commit/a97fdf
                if data[2:4] == b"\r\n":
                    # < pyinstaller 5.3
                    if self.pycMagic == b"\0" * 4:
                        self.pycMagic = data[0:4]
                    self._writeRawData(destination_entry + ".pyc", data)
                else:
                    # >= pyinstaller 5.3
                    if self.pycMagic == b"\0" * 4:
                        # if we don't have the pyc header yet, fix them in a later pass
                        self.barePycList.append(destination_entry + ".pyc")
                    self._writePyc(destination_entry + ".pyc", data)
            else:
                if not self.only_entrypoints:
                    self._writeRawData(destination_entry, data)

                    if entry.typeCmprsData in (b"z", b"Z"):
                        self._extractPyz(destination_entry)

        # Fix bare pyc's if any
        self._fixBarePycs()

    def _fixBarePycs(self):
        for pycFile in self.barePycList:
            with open(pycFile, "r+b") as pycFile:
                # Overwrite the first four bytes
                pycFile.write(self.pycMagic)

    def _writePyc(self, filename, data):
        with open(filename, "wb") as pycFile:
            pycFile.write(self.pycMagic)  # pyc magic

            if self.pymaj >= 3 and self.pymin >= 7:  # PEP 552 -- Deterministic pycs
                pycFile.write(b"\0" * 4)  # Bitfield
                pycFile.write(b"\0" * 8)  # (Timestamp + size) || hash

            else:
                pycFile.write(b"\0" * 4)  # Timestamp
                if self.pymaj >= 3 and self.pymin >= 3:
                    pycFile.write(b"\0" * 4)  # Size parameter added in Python 3.3

            pycFile.write(data)

    def _extractPyz(self, name):
        dirName = name + "_extracted"
        # Create a directory for the contents of the pyz
        if not os.path.exists(dirName):
            os.mkdir(dirName)

        with open(name, "rb") as f:
            pyzMagic = f.read(4)
            assert pyzMagic == b"PYZ\0"  # Sanity Check

            pyzPycMagic = f.read(4)  # Python magic value
            if self.pycMagic == b"\0" * 4:
                self.pycMagic = pyzPycMagic
            elif self.pycMagic != pyzPycMagic:
                self.pycMagic = pyzPycMagic
                log.warning("[!] pyc magic of files inside PYZ archive are different from those in CArchive")

            # Skip PYZ extraction if not running under the same python version
            if self.pymaj != sys.version_info.major or self.pymin != sys.version_info.minor:
                log.warning(
                    "[!] Warning: This script is running in a different Python version than the one used to build the executable."
                )
                log.info(
                    "[!] Please run this script in Python %d.%d to prevent extraction errors during unmarshalling.\nSkipping pyz extraction",
                    self.pymaj,
                    self.pymin,
                )
                return

            (tocPosition,) = struct.unpack("!i", f.read(4))
            f.seek(tocPosition, os.SEEK_SET)

            try:
                toc = marshal.load(f)
            except Exception as e:
                log.error("[!] Unmarshalling FAILED. Cannot extract %s. Extracting remaining files. Error: %s", name, str(e))
                return

            log.debug("[+] Found %d files in PYZ archive", len(toc))

            # From pyinstaller 3.1+ toc is a list of tuples
            if isinstance(toc, list):
                toc = dict(toc)

            for key in toc.keys():
                (ispkg, pos, length) = toc[key]
                f.seek(pos, os.SEEK_SET)
                fileName = key

                with suppress(Exception):
                    # for Python > 3.3 some keys are bytes object some are str object
                    fileName = fileName.decode("utf-8")

                # Prevent writing outside dirName
                fileName = fileName.replace("..", "__").replace(".", os.path.sep)
                if ispkg == 1:
                    filePath = os.path.join(dirName, fileName, "__init__.pyc")
                else:
                    filePath = os.path.join(dirName, fileName + ".pyc")

                fileDir = os.path.dirname(filePath)
                if not os.path.exists(fileDir):
                    os.makedirs(fileDir)

                try:
                    data = f.read(length)
                    data = zlib.decompress(data)
                except Exception as e:
                    print("[!] Error: Failed to decompress %s, probably encrypted. Extracting as is. Error: %s", filePath, str(e))
                    open(filePath + ".encrypted", "wb").write(data)
                else:
                    self._writePyc(filePath, data)


def main(kwargs):
    # kwargs = {"file": "path_to_file", "destination_folder": "path_where_to_extract", "entry_points": False/True}
    arch = PyInstArchive(kwargs)
    if arch.open() and arch.checkFile() and arch.getCArchiveInfo():
        arch.parseTOC()
        arch.extractFiles()
        arch.close()
        log.debug(
            "[+] Successfully extracted pyinstaller archive: %s\nYou can now use a python decompiler on the pyc files within the extracted directory",
            kwargs["file"],
        )
        return
    arch.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        prog="PyInstaller Extractor",
        description="PyInstaller Extractor is a Python script to extract the contents of a PyInstaller generated executable file.",
    )
    parser.add_argument("-f", "--file", action="store")
    parser.add_argument("-d", "--destination-folder", action="store", help="Folder to store extracted files")
    parser.add_argument("-e", "--entry-points", action="store_true", help="Extract only possible entry points")

    options = parser.parse_args()
    if not options.file or not os.path.exists(options.file):
        parser.print_help()
        sys.exit()

    # Convert to dict/kwargs
    options = vars(options)
    logging.basicConfig()
    log.setLevel(logging.DEBUG)
    main(options)
