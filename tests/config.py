from pathlib import Path

cwd = Path(__file__).parent.absolute()

# main
main_configuration = {
    "auth": "htpasswd",
    "userdb": "virtual",
    "storage": "Exim",
    "consumer": "Exim",
    "port": 0,
    "pidfile": "/tmp/pysieved.pid",
}

# TLS
tls_configuration = {}

# Virtual
storage_path = cwd.joinpath("mock_srv", "mail", "t", "test")
virtual_configuration = {
    "path": str(storage_path),
    "defaultdomain": "none.invalid",
    "uid": -1,
    "gid": -1,
}

# htpasswd
dovecot_passwords_path = cwd.joinpath("mock.passwd")
htpasswd_configuration = {
    "passwdfile": str(dovecot_passwords_path),
}

# Exim
exim_configuration = {
    "sendmail": "/usr/sbin/sendmail",
    "scripts": ".pysieved",
    "active": ".forward",
    "uid": -1,
    "gid": -1,
}

DEFAULT_CONFIG = {
    "main": main_configuration,
    "TLS": tls_configuration,
    "Virtual": virtual_configuration,
    "htpasswd": htpasswd_configuration,
    "Exim": exim_configuration,
}
