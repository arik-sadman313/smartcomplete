#!/usr/bin/env python3
"""Test only process detection; never apply patches or install/restart anything."""
from pathlib import Path
import subprocess
import unittest


class ProcessPreflight(unittest.TestCase):
    def run_case(self, implementation):
        source = Path(__file__).with_name('install.sh').read_text()
        start = source.index('if OLD_PID=$(pgrep ')
        end = source.index('sha256sum --check', start)
        script = ('set -Eeuo pipefail\n'
                  + 'pgrep() { ' + implementation + '; }\n'
                  + source[start:end]
                  + 'printf "CONTINUED:%s\\n" "$OLD_PID"\n')
        return subprocess.run(['bash', '-c', script], capture_output=True,
                              text=True, timeout=5, check=False)

    def test_stopped_is_allowed(self):
        result = self.run_case('return 1')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('CONTINUED:\n', result.stdout)

    def test_single_process_is_allowed(self):
        result = self.run_case('printf "1234\\n"')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('CONTINUED:1234', result.stdout)

    def test_multiple_processes_stop(self):
        result = self.run_case('printf "1234\\n5678\\n"')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Multiple Fcitx5', result.stderr)
        self.assertNotIn('CONTINUED:', result.stdout)

    def test_lookup_error_is_not_hidden(self):
        result = self.run_case('return 2')
        self.assertEqual(result.returncode, 2)
        self.assertIn('lookup failed', result.stderr)
        self.assertNotIn('CONTINUED:', result.stdout)


if __name__ == '__main__':
    unittest.main()
