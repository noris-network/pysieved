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
import re
import subprocess

import plugins
from plugins import FileStorage


class EximStorage(FileStorage.FileStorage):
    def __init__(self, sieve_test, mydir, active_file, homedir):
        self.sieve_test = sieve_test
        self.mydir = mydir
        self.active_file = active_file
        self.homedir = homedir
        self.basedir = os.path.join(self.homedir, self.mydir)
        self.active = os.path.join(self.homedir, self.active_file)
        self.sieve_hdr = "# Sieve filter"
        self.sieve_re = re.compile(r"^" + re.escape(self.sieve_hdr), re.S)

        # Create our directory if needed
        if not os.path.exists(self.basedir):
            os.mkdir(self.basedir)

        # If they already have a script, shuffle it into where we want it
        if os.path.exists(self.active) and not os.path.islink(self.active):
            try:
                with open(self.active) as file:
                    script = file.read()

                # Make sure this is an Exim Sieve filter
                if re.match(self.sieve_re, script, re.S):
                    os.rename(self.active, os.path.join(self.basedir, "exim"))
                    self.set_active("exim")
            except IOError:
                pass

    def __setitem__(self, k, v):
        if isinstance(v, bytes):
            v = v.decode()

        v = self.sieve_hdr + "\r\n" + v
        FileStorage.FileStorage.__setitem__(self, k, v)


class PysievedPlugin(plugins.PysievedPlugin):
    capabilities = (
        "envelope fileinto encoded-character "
        "enotify subaddress vacation copy "
        "comparator-i;ascii-casemap comparator-en;ascii-casemap "
        "comparator-i;octet comparator-i;ascii-numeric"
    )

    def init(self, config):
        self.sendmail = config.get("Exim", "sendmail", "/usr/sbin/sendmail")
        self.scripts_dir = config.get("Exim", "scripts", ".pysieved")
        self.active_file = config.get("Exim", "active", ".forward")
        self.uid = config.getint("Exim", "uid", -1)
        self.gid = config.getint("Exim", "gid", -1)

        # Drop privileges here if all users share the same uid/gid
        if self.gid >= 0:
            os.setgid(self.gid)
        if self.uid >= 0:
            os.setuid(self.uid)

    def exim_sieve_has_error(self, basedir, script):
        compiled = FileStorage.TempFile(basedir)
        compiled.close()

        sendmail = self.sendmail
        if isinstance(self.sendmail, bytes):
            sendmail = self.sendmail.decode()

        if isinstance(script, bytes):
            script = script.decode()

        command = [f"{sendmail} -bf {script} < /dev/null"]
        process = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE)

        error_str = "No errors with Exim"
        if process.stderr is not None:
            error_str = process.stderr.read().strip()

        if process.wait():
            return error_str

        return None

    def create_storage(self, params):
        return EximStorage(
            self.exim_sieve_has_error,
            self.scripts_dir,
            self.active_file,
            params["homedir"],
        )
