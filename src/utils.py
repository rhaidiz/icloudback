import sys
import logging
from pathlib import Path
from datetime import datetime
from icloudpy import ICloudPyService
from src.constants import SESSION_STORAGE_PATH
from src import get_logger

LOGGER = get_logger()

def get_icloud_api(username: str, password: str, cookie_directory=SESSION_STORAGE_PATH) -> ICloudPyService:
    """
    Obtain the icloudpy api object.
    """
    LOGGER.debug("porco dio")

    api = ICloudPyService(username, password, cookie_directory=cookie_directory)
    
    if api.requires_2fa:
        LOGGER.info("Two-factor authentication required.")
        code = input("Enter the code you received of one of your approved devices: ")
        result = api.validate_2fa_code(code)
        print("Code validation result: %s" % result)
    
        if not result:
            LOGGER.info("Failed to verify security code")
            sys.exit(1)
    
        if not api.is_trusted_session:
            LOGGER.debug("Session is not trusted. Requesting trust...")
            result = api.trust_session()
            LOGGER.debug("Session trust result %s" % result)
    
            if not result:
                LOGGER.info("Failed to request trust. You will likely be prompted for the code again in the coming weeks")
    return api


def create_snapshot_folder(root_folder):
    """
    Creates a new snapshot folder named with the current date in the format %Y-%m-%d-%H-%M-%S
        and returns it's path and the path to the latest folder.
    """

    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    current_snapshot_folder = f"{root_folder}/{timestamp}"
    Path(current_snapshot_folder).mkdir(parents=True, exist_ok=True)

    latest = f"{root_folder}/latest"

    if not Path(latest).exists():
        target_folder = current_snapshot_folder
        link_name = latest
        try:
            #os.symlink(target_folder, link_name)
            Path(link_name).symlink_to(target_folder)
            LOGGER.debug(f"Symlink created: {link_name} -> {target_folder}")
        except FileExistsError:
            LOGGER.error(f"Symlink already exists: {link_name}")
    return current_snapshot_folder, latest


def update_latest_symlink(current_folder, root_folder):
    """
    Updates the symblink to the new snapshot.
    """

    LOGGER.debug("Updating symlink...")
    target_folder = current_folder
    link_name = f"{root_folder}/latest"
    
    # Convert to Path objects for convenience
    link_path = Path(link_name)
    
    # Remove the symlink if it exists
    if link_path.is_symlink() or link_path.exists():
        link_path.unlink()
        LOGGER.debug(f"Removed existing symlink: {link_name}")
    
    # Create the new symlink
    link_path.symlink_to(target_folder, target_is_directory=True)
    LOGGER.debug(f"Created new symlink: {link_name} -> {target_folder}")
