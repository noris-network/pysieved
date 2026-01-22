import warnings
from pathlib import Path
from threading import Thread
from unittest import TestCase

from base import MockClient, MockConfig, MockFilesystem
from config import DEFAULT_CONFIG

from pysieved.main import Server, get_handler


class MockOptions:
    bindaddr = ""
    port = 0
    pidfile = "/tmp/pysieved.pid"
    base = str(Path(__file__).parent.joinpath("mock_srv"))
    tls_required = False
    tls_key = ""
    tls_cert = ""
    tls_passphrase = ""
    debug = True


class AuthenticateTest(TestCase):
    def setUp(self) -> None:
        super().setUp()

        options = MockOptions()
        config = MockConfig(DEFAULT_CONFIG)

        handler = get_handler(options, config)

        self.server = Server((options.bindaddr, options.port), handler)
        self._t = Thread(target=self.server.serve_forever)
        self._t.start()

        self.client = MockClient(self.server)

        # Ignore start up echoes
        self.client.get_full_response()

        self.username = "test"
        self.password = "12345"

    def tearDown(self) -> None:
        try:
            self.client.logout()
        finally:
            self.client.close()

        self.server.shutdown()
        self.server.server_close()
        self._t.join()

        super().tearDown()

    def test_authenticate(self) -> None:
        """Test authenticating to the server."""

        response = self.client.authenticate(self.username, self.password)
        self.assertEqual(response, b"OK\r\n")

    def test_authenticate_invalid_user(self) -> None:
        """Test authenticating to the server with a non-existing user."""

        response = self.client.authenticate("does-not-exist", self.password)

        expected_response = b'NO "Bad username or password"\r\n'
        self.assertEqual(response, expected_response)

    def test_authenticate_wrong_password(self) -> None:
        """Test authenticating to the server with a wrong password."""

        response = self.client.authenticate(self.username, "wrong-password")

        expected_response = b'NO "Bad username or password"\r\n'
        self.assertEqual(response, expected_response)


class ManagesieveTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        options = MockOptions()
        config = MockConfig(DEFAULT_CONFIG)

        handler = get_handler(options, config)

        cls.server = Server((options.bindaddr, options.port), handler)
        cls._t = Thread(target=cls.server.serve_forever)
        cls._t.start()

        cls.username = "test"
        cls.password = "12345"
        cls.filter_name = "test_filter"
        cls.filter_content = b"# Sieve filter\n# Test filter\n"
        cls.OK = b"OK\r\n"

        cls.fs = MockFilesystem(options.base, cls.username)
        cls.client = MockClient(cls.server)

        # Ignore start up echoes
        cls.client.get_full_response()

        # Add a test script to the filesystem.
        # It is removed in the teardown
        created = cls.fs.create_filter(cls.filter_name, cls.filter_content)
        if not created:
            warnings.warn(f"Test filter '{cls.filter_name}' already exists.")

    @classmethod
    def tearDownClass(cls) -> None:
        # Remove initial test filter
        # removed = cls.fs.remove_filter(cls.filter_name)
        # if not removed:
        #     warnings.warn(f"Could not remove filter '{cls.filter_name}'.")

        try:
            cls.client.logout()
        finally:
            cls.client.close()

        cls.server.shutdown()
        cls.server.server_close()
        cls._t.join()

        super().tearDownClass()

    def test_listscripts(self) -> None:
        """Test that valid scripts are listed."""

        self.client.authenticate(self.username, self.password)

        response = self.client.listscripts()

        self.assertIn(self.filter_name.encode(), response)
        self.assertTrue(response.endswith(self.OK))

    def test_capability(self) -> None:
        """Test that the CAPABILITY command returns a valid response."""

        response = self.client.capability()

        lines = response.split(b"\r\n")

        expected_sieve = b'"SIEVE" "envelope fileinto encoded-character enotify subaddress vacation copy comparator-i;ascii-casemap comparator-en;ascii-casemap comparator-i;octet comparator-i;ascii-numeric"'
        self.assertEqual(lines[0], b'"IMPLEMENTATION" "pysieved 1.0"')
        self.assertEqual(lines[1], b'"SASL" "PLAIN"')
        self.assertEqual(lines[2], expected_sieve)
        self.assertEqual(lines[3], b"OK")

    def test_havespace(self) -> None:
        """Test a valid HAVESPACE command."""

        self.client.authenticate(self.username, self.password)

        response = self.client.havespace("mock_script", 1)
        self.assertEqual(response, self.OK)

    def test_havespace_not_a_number(self) -> None:
        """Test an invalid HAVESPACE command."""

        self.client.authenticate(self.username, self.password)

        response = self.client.havespace("mock_script", "not-a-number")
        self.assertEqual(response, b'NO "Not a number"\r\n')

    def test_havespace_exceeds_quota(self) -> None:
        """Test an valid HAVESPACE command with a very large byte size."""

        self.client.authenticate(self.username, self.password)

        response = self.client.havespace("mock_script", 999_999_999_999)
        self.assertEqual(response, b'NO (QUOTA) "Quota exceeded"\r\n')

    def test_putscript(self) -> None:
        """Test a valid PUTSCRIPT command with the correct size."""

        self.client.authenticate(self.username, self.password)

        filter_name = "putscript_test"

        response = self.client.putscript(filter_name, b"# This is a test")
        self.assertEqual(response, self.OK)
        self.assertTrue(self.fs.has_filter(filter_name))

        content = self.fs.get_filter(filter_name)
        if content is None:
            raise Exception(f"Could not read content for '{filter_name}'.")

        self.assertEqual(len(content), 32)
        self.assertEqual(content, b"# Sieve filter\n# This is a test\n")

        removed = self.fs.remove_filter(filter_name)
        self.assertTrue(removed)

    def test_setactive(self) -> None:
        """Test the SETACTIVE command on the test script."""

        self.client.authenticate(self.username, self.password)

        # Activate the script
        response = self.client.setactive(self.filter_name)
        self.assertEqual(response, self.OK)

        filters = self.client.listscripts()
        has_active = any(line.endswith(b"ACTIVE") for line in filters.split(b"\r\n"))
        self.assertTrue(has_active, "Script was not activated")

        # Deactivate the script
        response = self.client.setactive()
        self.assertEqual(response, self.OK)

        filters = self.client.listscripts()
        has_active = any(line.endswith(b"ACTIVE") for line in filters.split(b"\r\n"))
        self.assertFalse(has_active, "Script was not deactivated")

        # Re-activate for other tests
        self.client.setactive(self.filter_name)

    def test_setactive_invalid_script(self) -> None:
        """Test the SETACTIVE command without giving a filter name."""

        self.client.authenticate(self.username, self.password)

        response = self.client.setactive("does-not-exist")
        self.assertEqual(response, b'NO "No script by that name"\r\n')

    def test_getscript(self) -> None:
        """Test the GETSCRIPT command with a valid filter name."""

        self.client.authenticate(self.username, self.password)

        response = self.client.getscript(self.filter_name)
        self.assertTrue(response.endswith(self.OK))

        lines = response.split(b"\r\n")
        byte_size, content, ok = lines[:-1]

        self.assertEqual(byte_size, b"{29}")

        self.assertEqual(content, b"# Sieve filter\n# Test filter\n")
        self.assertEqual(ok, b"OK")

        self.assertEqual(response, b"{29}\r\n# Sieve filter\n# Test filter\n\r\nOK\r\n")

    def test_getscript_invalid_script(self) -> None:
        """Test the GETSCRIPT command with a non-existing filter name."""

        self.client.authenticate(self.username, self.password)

        response = self.client.getscript("does-not-exist")
        self.assertEqual(response, b'NO "No script by that name"\r\n')

    def test_deletescript(self) -> None:
        """Test the DELETESCRIPT command on a valid filter."""

        self.client.authenticate(self.username, self.password)

        # Deactivate script
        self.client.setactive()

        # Send the delete command
        response = self.client.deletescript(self.filter_name)
        self.assertEqual(response, self.OK)

        # Recreate script and reactivate script
        self.fs.create_filter(self.filter_name, self.filter_content)
        self.client.setactive(self.filter_name)

    def test_deletescript_invalid_script(self) -> None:
        """Test the DELETESCRIPT command with a non-existing filter name."""

        self.client.authenticate(self.username, self.password)

        response = self.client.deletescript("does-not-exist")
        self.assertEqual(response, b'NO "No script by that name"\r\n')

    def test_deletescript_active_script(self) -> None:
        """Test the DELETSCRIPT command on an active script."""

        self.client.authenticate(self.username, self.password)

        # Activate script
        self.client.setactive(self.filter_name)

        # Try to delete script
        response = self.client.deletescript(self.filter_name)
        self.assertEqual(response, b'NO "Script is active"\r\n')
