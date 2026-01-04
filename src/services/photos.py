import os
import queue
import logging
import threading
from pathlib import Path
from shutil import copyfileobj

from src import get_logger

photo_task_queue = queue.Queue()

LOGGER = get_logger()

class PhotoItem:
    def __init__(self, photo):
        self.photo = photo

def icloud_photos_worker(thread_id, photo, api, current_path, latest):
    try:
        # photo = photo_task_queue.get(timeout=3)
        LOGGER.debug(f"Processing {photo.filename} {photo.created.year}/{photo.created.month}/{photo.created.day}")

        download = photo.download()
        local_file_path = f"{current_path}/{photo.created.year}/{photo.created.month}/{photo.created.day}/"
        old_file_path = f"{latest}/{photo.created.year}/{photo.created.month}/{photo.created.day}/"

        created_date = photo.created
        # use the date to create a folder
        Path(f"{local_file_path}/").mkdir(parents=True, exist_ok=True)

        local_file = f"{local_file_path}/{photo.filename}"
        old_file = f"{old_file_path}/{photo.filename}"

        if not Path(old_file).exists():
            # an old version of this file does not exist, download it.
            try:
                with open(local_file, 'wb') as opened_file:
                    copyfileobj(download.raw, opened_file)
            except Exception as err:
                LOGGER.error(f"Cannot download {local_file} - {err}")
        else:
            # an old file exists so chek if we should download it or hardlink it
            local_file_size = os.path.getsize(old_file)
            remote_file_size = photo.size
            if local_file_size == remote_file_size:
                # no changed, create hardlink
                LOGGER.debug(f"No changes for {local_file} create hardlink")
                Path(local_file).hardlink_to(old_file)
            else:
                LOGGER.debug(f"Downloading updated version of {local_file}")
                try:
                    with open(local_file, 'wb') as opened_file:
                        copyfileobj(download.raw, opened_file)
                except Exception as err:
                    LOGGER.error(f"Cannot download {local_file} - {err}")
        # photo_task_queue.task_done()
    except Exception as err:
        LOGGER.error(f"Thread {thread_id} - {err}")

def icloud_photos_album_worker(thread_id, api, album, current_folder):

    LOGGER.debug(f"Processing album {album}")

    local_album_path = f"{current_folder}/{album}"

    Path(local_album_path).mkdir(parents=True, exist_ok=True)
    remote_album = api.photos.albums[album]

    for photo in remote_album:
        local_album_file_folder_path = f"{local_album_path}/{photo.created.year}/{photo.created.month}/{photo.created.day}"
        Path(local_album_file_folder_path ).mkdir(parents=True, exist_ok=True)

        local_album_file_path = f"{local_album_file_folder_path}/{photo.filename}"
        local_all_photo_file_path = f"{current_folder}/allphotos/{photo.created.year}/{photo.created.month}/{photo.created.day}/{photo.filename}"
        if Path(local_all_photo_file_path).exists():
            LOGGER.debug(f"[{thread_id}] Found photo {photo.filename} in album {album} create hardlink")
            try:
                Path(local_album_file_path).hardlink_to(local_all_photo_file_path)
            except Exception as err:
                LOGGER.error(f"[{thread_id}] Error creating hardlink for {photo.filename} in album {album} {err}")
        else:
            LOGGER.error(f"[{thread_id}] Not found {photo.filename} in album {album}")

def icloud_photos_downloader(api, current_folder, latest, threads_count):
    """
    Handles the download of iCloud Drive.
    """
    LOGGER.info("Start iCloud Photos downloader")
    # api = get_icloud_api()
    photos_local_path = "photos/allphotos"

    current_all_photos_folder = f"{current_folder}/{photos_local_path}/"
    latest = f"{latest}/{photos_local_path}/"

    Path(current_folder).mkdir(parents=True, exist_ok=True)

    num_threads = threads_count

    threads = []

    for photo in api.photos.all:

        if num_threads != 0:
            t = threading.Thread(target=icloud_photos_worker, args=(num_threads, photo, api, current_all_photos_folder ,latest,))
            num_threads = num_threads - 1
            t.start()
            threads.append(t)

        # Wait for all threads to finish
        if num_threads == 0:
            for t in threads:
                t.join()
            num_threads = 5

    # after the for, wait for any remaining thread
    for t in threads:
        t.join()

    num_threads = 5

    threads = []

    current_album_folder = f"{current_folder}/photos/"
    # Now I need to preserve the album organization
    for album in api.photos.albums:
        if num_threads != 0 and album != "All Photos":
            t = threading.Thread(target=icloud_photos_album_worker, args=(num_threads, api, album, current_album_folder,))
            num_threads = num_threads - 1
            t.start()
            threads.append(t)

        if num_threads == 0:
            for t in threads:
                t.join()
            num_threads = 5
                                     
    # after the for, wait for any remaining thread
    for t in threads:
        t.join()

    LOGGER.info("iCloud Photos downloader finished")
