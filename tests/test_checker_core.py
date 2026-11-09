import imaplib
import socket
import unittest
from checker_core import parse_line, check_imap


class ParsingTests(unittest.TestCase):
    def test_password_is_preserved(self):
        self.assertEqual(parse_line(' User@example.com: p:a:ss  \n'), ('User@example.com', ' p:a:ss  '))

    def test_invalid_records(self):
        for line in ('# comment', '', 'user@example.com', 'user@example.com:', 'a@../test:pw', 'a@bad..com:pw', 'a@domain.com/path:pw'):
            with self.subTest(line=line):
                self.assertIsNone(parse_line(line))


class IMAPTests(unittest.TestCase):
    def test_success_and_logout(self):
        class Client:
            def __init__(self, host, port, timeout, ssl_context):
                self.args = (host, port, timeout)
                self.context = ssl_context
                clients.append(self)
            def login(self, address, password):
                self.credentials = address, password
                return 'OK', [b'welcome']
            def logout(self):
                self.closed = True
        clients = []
        self.assertEqual(check_imap('a@b.com', 'p:word', ('imap.b.com', '993'), 7, Client), 'valid')
        self.assertEqual(clients[0].credentials, ('a@b.com', 'p:word'))
        self.assertEqual(clients[0].args, ('imap.b.com', 993, 7))
        self.assertTrue(clients[0].closed)
        self.assertTrue(clients[0].context.check_hostname)

    def test_connection_protocol_error_is_not_an_invalid_password(self):
        def factory(*args, **kwargs):
            raise imaplib.IMAP4.error('bad greeting')
        self.assertEqual(check_imap('a@b.com', 'pw', ('host', 993), 5, factory), 'error')

    def test_auth_failure_and_abort_are_distinct(self):
        for error, expected in ((imaplib.IMAP4.error('no'), 'invalid'), (imaplib.IMAP4.abort('lost'), 'error'), (socket.timeout(), 'error')):
            class Client:
                def __init__(self, *args, **kwargs): pass
                def login(self, *args): raise error
                def logout(self): pass
            with self.subTest(expected=expected):
                self.assertEqual(check_imap('a@b.com', 'pw', ('host', 993), 5, Client), expected)

if __name__ == '__main__':
    unittest.main()
