"""Run explicitly inside the built image: python -m unittest -v test_container."""

import importlib
import shutil
import subprocess
import unittest
from pathlib import Path

# Host pytest cannot verify the production image's packages or filesystem.
__test__ = False


class ContainerTests(unittest.TestCase):
    """Check the image through its production entrypoint without network access."""

    def test_git_runs(self):
        """Git must survive removal of the temporary build packages."""
        result = subprocess.run(
            ["git", "--version"], check=True, capture_output=True, text=True
        )
        self.assertTrue(result.stdout.startswith("git version "), result.stdout)

    def test_application_imports(self):
        """Production imports must work without development packages or downloads."""
        module = importlib.import_module("evergreen")
        self.assertTrue(callable(module.main))

    def test_build_packages_are_absent(self):
        """Compilation dependencies must not remain in the shipped image."""
        self.assertIsNone(shutil.which("gcc"))
        for package in ("gcc", "libc6-dev", "libffi-dev"):
            with self.subTest(package=package):
                result = subprocess.run(
                    ["dpkg-query", "-W", "-f=${db:Status-Status}", package],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertIn(result.returncode, (0, 1), result.stderr)
                self.assertNotEqual(result.stdout.strip(), "installed", package)

    def test_apt_indexes_are_absent(self):
        """Package indexes must not add files to the shipped image."""
        lists = Path("/var/lib/apt/lists")
        self.assertFalse([str(path) for path in lists.rglob("*") if path.is_file()])


if __name__ == "__main__":
    unittest.main()
