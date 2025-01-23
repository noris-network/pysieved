#! /usr/bin/python

## pysieved - Python managesieve server
## Copyright (C) 2007 Neale Pickett

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or (at
## your option) any later version.

## This program is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
## USA
#
# 22 January 2025 - Modified by F. Ioannidis.


import os
import sys


def daemon(pidfile=None, stdout=None, stderr=None):
    # Do this first so errors print out right away
    if pidfile:
        f = open(pidfile, "w")
    else:
        f = None

    pid = os.fork()
    if pid:
        # Exit first parent
        os._exit(0)

    # Decouple from parent
    os.setsid()

    # Second fork
    pid = os.fork()
    if pid:
        # Exit second parent
        os._exit(0)

    # Remap std files
    os.close(0)
    if stdout:
        sys.stdout = stdout
    os.close(1)
    if stderr:
        sys.stderr = stderr
    os.close(2)

    # Write pid
    if f:
        f.write(str(os.getpid()))
        f.close()
