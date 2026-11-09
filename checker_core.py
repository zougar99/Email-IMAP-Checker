"""Shared, non-destructive input parsing and IMAP connection helpers."""
import imaplib
import re
import ssl

# Deliberately conservative: accept ordinary mailbox addresses, not every RFC form.
_ADDRESS = re.compile(r"^[^\s@:/\\]+@(?:[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?\.)+[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?$")


def parse_line(line):
    """Return (address, password), or None for comments and malformed records.

    Only the first colon separates the address from the password. Passwords are
    otherwise left untouched, including whitespace and additional colons.
    """
    line = line.rstrip('\r\n')
    if not line.strip() or line.lstrip().startswith('#') or ':' not in line:
        return None
    address, password = line.split(':', 1)
    address = address.strip()
    if not _ADDRESS.fullmatch(address) or not password:
        return None
    return address, password


def check_imap(address, password, host, timeout, client_factory=None):
    """Check one account; distinguish rejected credentials from network errors."""
    client = None
    factory = client_factory or imaplib.IMAP4_SSL
    try:
        try:
            client = factory(host[0], int(host[1]), timeout=timeout,
                             ssl_context=ssl.create_default_context())
        except (imaplib.IMAP4.error, OSError, ValueError, ssl.SSLError):
            return 'error'
        try:
            status, _ = client.login(address, password)
            return 'valid' if status == 'OK' else 'invalid'
        except imaplib.IMAP4.abort:
            return 'error'
        except imaplib.IMAP4.error:
            return 'invalid'
        except (OSError, ssl.SSLError, ValueError):
            return 'error'
    finally:
        if client is not None:
            try:
                client.logout()
            except (imaplib.IMAP4.error, OSError, EOFError):
                pass
