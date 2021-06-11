## Introduction

Gateway that shares different USB sticks and SARAD instruments with integrated
FT232R serial to USB converter through RFC2217.

## Features

The program has the following features:

- Detects plugged and unplugged USB sticks and SARAD instruments (udev)
- Shares the USB stick serial connection through RFC2217
- Announces the RFC2217 connection to the rest of the network (mDNS)

## Installation and usage

For test and development, the program is prepared to run in a virtual environment.

### Installation ###

    git clone <bare_repository>

to clone the working directory from the git repository.

    cd src-instrumentserver2-rfc2217
    bin/env-create

to create the directory with the virtual environment.

    bin/activate

to activate the virtual environment.

### Usage ###

    bin/rfc2217-gateway

to start the program.

After attaching a SARAD instrument you should see log messages indicating that a
device was detected and connected to a port.

## Author

(c) 2020 [Aitor Iturrioz](https://github.com/bodiroga)

## License
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
