from logging import root
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
from datetime import datetime
from src.utils import create_snapshot_folder, update_latest_symlink

class TestUtils(unittest.TestCase):
    """ Test the utils functions."""

    def test_creates_snapshot_and_latest_symlink(self):
        """ Test the creation of a snapshot folder. """

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            snapshot_path, latest_path = create_snapshot_folder(str(root))

            expected_snapshot = Path(snapshot_path) # root / expected_timestamp
            self.assertTrue(expected_snapshot.exists())
            self.assertTrue(expected_snapshot.is_dir())

            latest = root / "latest"
            self.assertEqual(latest_path, str(latest))
            self.assertTrue(latest.exists())
            self.assertTrue(latest.is_symlink())
            self.assertEqual(latest.resolve(), expected_snapshot)

    def test_update_latest_symlink(self):
        """ Test the update of the symlink latest. """

        with tempfile.TemporaryDirectory() as current_folder:
            with tempfile.TemporaryDirectory() as root_folder:
                update_latest_symlink(current_folder, root_folder)

                expected_path = f"{root_folder}/latest"
                expected_sym_link = Path(expected_path)
                self.assertTrue(expected_sym_link.exists())
                self.assertTrue(expected_sym_link.is_symlink())
                self.assertEqual(expected_sym_link.resolve(), Path(current_folder))

if __name__ == "__main__":
    unittest.main()
