from logging import root
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
from datetime import datetime
from src.utils import create_snapshot_folder, update_latest_symlink
from src import Config

class TestConfig(unittest.TestCase):
    """ Test the config functions."""

    def test_config_file_exists(self):
        """ Test if the configuration file exists. """

        with tempfile.TemporaryFile() as config_file:

            config = Config(config_path=str(config_file))
            self.assertIsNotNone(config)

if __name__ == "__main__":
    unittest.main()
