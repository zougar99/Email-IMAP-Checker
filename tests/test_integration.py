"""Offline integration tests for the legacy CLI and its writers."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def test_results_progress_and_unchanged_input(self):
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            (work / 'hoster.dat').write_text('example.com:imap.example.com:993\n', encoding='utf-8')
            original = '# comment\nvalid@example.com:pwd:with:colon  \ninvalid@example.com:pw\nerror@example.com:pw\nunknown@else.test:pw\ninvalid line\n'
            (work / 'input.txt').write_text(original, encoding='utf-8')
            # Replace the network operation before the CLI imports it.
            (work / 'sitecustomize.py').write_text(
                "import checker_core\n"
                "checker_core.check_imap = lambda address, password, host, timeout: address.split('@')[0]\n",
                encoding='utf-8')
            env = os.environ.copy()
            env['PYTHONPATH'] = os.pathsep.join((temp, str(ROOT)))
            proc = subprocess.run([sys.executable, str(ROOT / 'atr3.py'), '-i', 'input.txt', '-t', '2'],
                                  cwd=work, env=env, capture_output=True, text=True, timeout=20)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual((work / 'input.txt').read_text(encoding='utf-8'), original)
            self.assertIn('valid=1 invalid=1 error=1 unmatched=1', proc.stdout)
            run = next((work / 'M-P-V-I').iterdir())
            self.assertEqual((run / 'mail_errors.txt').read_text(), 'error@example.com\n')
            self.assertEqual((run / 'mail_pass_invalid.txt').read_text(), 'invalid@example.com\n')
            self.assertEqual((run / 'mail_unmatched.txt').read_text(), 'unknown@else.test\n')
            self.assertEqual((run / 'valid_with_passwords' / 'mail_pass_valid_with_password.txt').read_text(), 'valid@example.com:pwd:with:colon  \n')
            self.assertEqual((work / 'isp+boite' / 'mail_example.com.txt').read_text(), 'valid@example.com\n')

    def test_disabled_invalid_output(self):
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            (work / 'input.txt').write_text('a@unknown.invalid:pw\n')
            (work / 'hoster.dat').write_text('')
            proc = subprocess.run([sys.executable, str(ROOT / 'atr3.py'), '-i', 'input.txt', '-t', '1', '-iu', 'False'],
                                  cwd=work, capture_output=True, text=True, timeout=10)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            run = next((work / 'M-P-V-I').iterdir())
            self.assertFalse((run / 'mail_unmatched.txt').exists())
            self.assertIn('unmatched=1', proc.stdout)

    def test_missing_input_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            proc = subprocess.run([sys.executable, str(ROOT / 'atr3.py'), '-i', 'missing.txt'],
                                  cwd=temp, capture_output=True, text=True, timeout=10)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn('input file does not exist', proc.stderr)

if __name__ == '__main__':
    unittest.main()
