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
# 24 January 2025 - Modified by F. Ioannidis.


from crypt import crypt

from pysieved import plugins


class PysievedPlugin(plugins.PysievedPlugin):
    def init(self, config):
        self.passfile = config.get("htpasswd", "passwdfile", "/etc/exim/virtual/passwd")

        with open(self.passfile) as file:
            lines = file.readlines()

        self.passwd = {}
        for line in lines:
            parts = line.rstrip().split(":", 1)
            self.passwd[parts[0]] = parts[1]

    def auth(self, params):
        try:
            cpass = self.passwd[params["username"]]
        except KeyError:
            return False

        return cpass == crypt(params["password"], cpass[:2])
