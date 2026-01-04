import os
import yaml
from src.constants import DEFAULT_CONFIG_FILE_NAME

class Config:
    """
    Represents the configuration for this backup.
    """

    def __init__(self, config_path=DEFAULT_CONFIG_FILE_NAME):
        """Read config file."""
        if not (config_path and os.path.exists(config_path)):
            return None

        with open(file=config_path, encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file)

        self.config = config

    @property
    def logger_level(self):
        return self.config['logger']['level']

    @property
    def logger_filename(self):
        return self.config['logger']['filename']

    @property
    def username(self) -> str:
        """ Retrieve the username from the config."""
        return self.config['credentials']['username']
    
    @property
    def password(self) -> str:
        """ Retrieve the password from the config."""
        return self.config['credentials']['password']
    
    @property
    def root_path(self) -> str:
        return self.config['root']
    
    @property
    def drive_list_ignore(self) -> list[str]:
        return self.config['drive']['ignore']

    @property
    def threads_count(self) -> int:
        return self.config['threads_count']
    
