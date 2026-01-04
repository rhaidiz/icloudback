import src.utils as utils
from src.config import Config
from src.services import drive, photos
from src import configure_logger, get_logger
import sys


if __name__ == "__main__":

    config = Config()

    if config == None:
        sys.exit()

    configure_logger(config)

    LOGGER = get_logger()

    LOGGER.info("Starting iCloud backup.")

    api = utils.get_icloud_api(config.username, config.password)

    # set root download folder
    root_folder = config.root_path

    # create current snapshot folder
    current_folder, latest = utils.create_snapshot_folder(root_folder)

    # start downloading icloud_drive
    drive.icloud_drive_downloader(api, current_folder, latest, config.drive_list_ignore, config.threads_count)

    # download icloud photos
    photos.icloud_photos_downloader(api, current_folder, latest, config.threads_count)

    # update symlink
    utils.update_latest_symlink(current_folder, root_folder)
