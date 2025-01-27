# 22 January 2025 - Modified by F. Ioannidis.

import os
import re

from pysieved import plugins

path_re = re.compile(r"%((\d+)(\.\d+)?)?([ud%])")


class PysievedPlugin(plugins.PysievedPlugin):
    def init(self, config):
        self.uid = config.getint("Virtual", "uid", None)
        self.gid = config.getint("Virtual", "gid", None)
        self.defaultdomain = config.get("Virtual", "defaultdomain", "none")
        self.path = config.get("Virtual", "path", None)
        assert (self.uid is not None) and (self.gid is not None) and self.path

    def lookup(self, params):
        if self.gid >= 0:
            os.setgid(self.gid)
        if self.uid >= 0:
            os.setuid(self.uid)

        try:
            user, domain = params["username"].split("@", 1)
        except ValueError:
            user, domain = params["username"], self.defaultdomain

        def repl(m):
            l = m.group(2)
            r = m.group(3)
            c = m.group(4)
            if c == "%":
                return "%"
            elif c == "u":
                s = user
            elif c == "d":
                s = domain
            if l:
                l = int(l)
                if r:
                    r = int(r[1:])
                    return s[l : l + r]
                else:
                    return s[:l]
            else:
                return s

        username = path_re.sub(repl, self.path)
        return username


if __name__ == "__main__":
    c = plugins.TestConfig(
        uid=-1,
        gid=-1,
        defaultdomain="woozle.snerk",
        path="/shared/spool/active/%d/%0.1u/%1.1u/%u/sieve/",
    )
    n = PysievedPlugin(None, c)
    print(n.lookup({"username": "neale@woozle.org"}))
