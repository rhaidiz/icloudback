import time
import os
import logging
import queue
import threading
from pathlib import Path
from shutil import copyfileobj

from src import get_logger

# Define a queue
task_queue = queue.Queue()

LOGGER = get_logger()

"""The item in the queue that will be processed."""
class QueueItem:
    def __init__(self, local_path, remote_file_name, remote_parent):
        self.local_path = local_path
        self.remote_file_name = remote_file_name
        self.remote_parent = remote_parent

# Wo function that consumes items from the queue
def icloud_drive_worker(thread_id, current_path, latest, list_ignore):
    while True:
        try:
            # Get a task from the queue with timeout to allow graceful exit
            task = task_queue.get(timeout=3)
            remote_parent = task.remote_parent
            remote_file_name = task.remote_file_name
            local_path = task.local_path

            node = remote_parent[remote_file_name]
            LOGGER.info(f"Processing file {local_path}/{remote_file_name}")

            if node.type == 'folder':
                if node.name in list_ignore: 
                    LOGGER.debug(f"Skip {node.name} in ignore list.")
                    continue
                # Create the folder locally
                LOGGER.debug(f"create folder {local_path}/{remote_file_name}")
                Path(f"{current_path}/{local_path}/{remote_file_name}").mkdir(parents=True, exist_ok=True)

                # Add all the children of this folder in the queue
                for d in node.dir():
                    task_queue.put(QueueItem(f"{task.local_path}/{task.remote_file_name}", d, node ))

            elif node.type == 'file':
                # this is a file, before downloading it, check in latest is the file exists
                # if the file exists and is not different, make a symlink
                # if the file exists and is different, download it new

                old_local_file_path = f"{latest}/{local_path}/{remote_file_name}"
                new_local_file_path = f"{current_path}/{local_path}/{remote_file_name}"

                # Let's also make sure that the folder exists.
                Path(f"{current_path}/{local_path}").mkdir(parents=True, exist_ok=True)

                LOGGER.info(f"Processing file {local_path}/{remote_file_name}")

                # File in latest does not exist
                if not Path(old_local_file_path).exists():
                    LOGGER.debug("File does not exist in latest, download it.")
                    try:
                        with node.open(stream=True) as response:
                            with open(new_local_file_path, 'wb') as file_out:
                                copyfileobj(response.raw, file_out)
                        item_modified_time = time.mktime(node.date_modified.timetuple())
                        os.utime(new_local_file_path, (item_modified_time, item_modified_time))
                    except Exception as e:
                        LOGGER.error(f"Error downloading file {new_local_file_path} with error {e}")

                else:
                    # an old file exists so check if we should download or hardlink it
                    local_file_modified_time = int(os.path.getmtime(old_local_file_path))
                    remote_file_modified_time = int(node.date_modified.timestamp())
                    local_file_size = os.path.getsize(old_local_file_path)
                    remote_file_size = node.size
                    if local_file_modified_time == remote_file_modified_time and (
                        local_file_size == remote_file_size
                        or (local_file_size == 0 and remote_file_size is None)
                        or (local_file_size is None and remote_file_size == 0)
                    ):
                        LOGGER.debug(f"No changes for {new_local_file_path} create hardlink")
                        Path(new_local_file_path).hardlink_to(old_local_file_path)
                    else:
                        # download file
                        LOGGER.debug(f"Downloading updated version of {new_local_file_path}")
                        try:
                            with node.open(stream=True) as response:
                                with open(new_local_file_path, 'wb') as file_out:
                                    copyfileobj(response.raw, file_out)
                            item_modified_time = time.mktime(node.date_modified.timetuple())
                            os.utime(new_local_file_path, (item_modified_time, item_modified_time))
                        except Exception as e:
                            LOGGER.error(f"Error downloading new version of file {new_local_file_path} with error {e}")
            else:
                # should not be here
                LOGGER.error(f"Should not be here {node.type}")
            task_queue.task_done()  # Mark task as done
        except queue.Empty:
            LOGGER.info(f"Thread {thread_id} found queue empty, exiting.")
            break

def icloud_drive_downloader(api, current_folder, latest, list_ignore, threads_count):
    """
    Handles the download from iCloud Drive.
    """

    LOGGER.info("Start iCloud downloader")
    # api = get_icloud_api()
    drive_local_path = "drive"

    Path(f"{current_folder}/{drive_local_path}/").mkdir(parents=True, exist_ok=True)
    root_node = api.drive
    for f in root_node.dir():
        task_queue.put(QueueItem(drive_local_path, f, root_node))

    # Create and start threads
    threads = []
    for i in range(threads_count):
        t = threading.Thread(target=icloud_drive_worker, args=(i, current_folder, latest, list_ignore,))
        t.start()
        threads.append(t)

    LOGGER.debug("Waiting to process all threads")
    # Wait for all threads to finish
    for t in threads:
        t.join()

    LOGGER.info("iCloud downloader finished!")
