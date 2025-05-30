# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Changed

#### 2025-01-22

* Upgraded project to work with python 3.11 for **some** plugins.
* `./config.py`: Updated exception handling to avoid using bare excepts.
* `./daemon.py`: Converted `file` to `open`, as it works in Python 3.
* `./managesieve.py`: Fixed some formatting, changed server `read` and `write` handlers to work with strings and bytes correctly.
* `./pysieved.py`: Fixed imports and removed 2 semicolons.
* `./plugins/__init__.py`: Updated `base64` decoding in authentication for Python 3. Some formatting changes.
* `./plugins/exim.py`: Updated subprocess procedure to work for Python 3, updated imports, used context manager for file handling, updated EximStorage to allow `bytes` as values.
* `./plugins/FileStorage.py`: Updated imports, urllib `quote` and `unquote` methods, allowed writing `str` types in `write_out`, used context manager for file handling.
* `./plugins/htpasswd.py`: Used context manager for reading file with credentials. Some formatting changes.
* `./plugins/virtual.py`: Updated imports and made some formatting changes

#### 2025-01-23

* Moved all source files and plugins into a python package:
    * `./managesieve.py` -> `./pysieved/managesieve.py.py`
    * `./pysieved.py` -> `./pysieved/main.py`
    * `./daemon.py` -> `./pysieved/daemon.py`
    * `./config.py` -> `./pysieved/config.py`
    * `./plugins/virtual.py` -> `./pysieved/plugins/virtual.py`
    * `./plugins/sasl.py` -> `./pysieved/plugins/sasl.py`
    * `./plugins/passwd.py` -> `./pysieved/plugins/passwd.py`
    * `./plugins/pam.py` -> `./pysieved/plugins/pam.py`
    * `./plugins/mysql.py` -> `./pysieved/plugins/mysql.py`
    * `./plugins/htpasswd.py` -> `./pysieved/plugins/htpasswd.py`
    * `./plugins/FileStorage.py` -> `./pysieved/plugins/FileStorage.py`
    * `./plugins/exim.py` -> `./pysieved/plugins/exim.py`
    * `./plugins/dovecot.py` -> `./pysieved/plugins/dovecot.py`
    * `./plugins/accept.py` -> `./pysieved/plugins/accept.py`
    * `./plugins/__init__.py` -> `./pysieved/plugins/__init__.py`
* Updated imports in the following files after converting to a Python package:
    * `./pysieved/main.py`
    * `./pysieved/plugins/virtual.py`
    * `./pysieved/plugins/FileStorage.py`
    * `./pysieved/plugins/exim.py`

#### 2025-01-24

* Added debian packaging
  * Added the folder `./debian/`, containing the necessary files to build a debian package for the application
  * Added the folder `./default/` and a file in `./default/pysieved`, containing the options to run the application through debian
  * Added `./Dockerfile`, which creates a docker image to build the debian package in
  * Added the executable `./build_deb.sh` script, which uses the docker image to build and extract the debian package from
  * Updated `./setup.py`, fixing the entrypoint to point to the new filename
  * Fixed imports in `./pysieved/main.py`
  * Fixed imports in `./pysieved/plugins/htpasswd.py`
* Updated `./.gitignore`, to ignore locally built debian packages

#### 2025-02-19

* Added `./.github/workflows/build-deb.yml` file to build and release debian package with Github Actions
* Updated `./debian/build_deb.sh` script to automatically update the debian changelog  before building the debian package

#### 2025-05-30

* `./pysieved/main.py`: Enabled listening to IPv6 addresses in `class Server(SocketServer.ForkingTCPServer)`.
