# iCloudBack

iCloudBack is a simple software to perform backups of your iCloud data. It solves my problem of taking incremental snapshot-like backups of my iCloud. It currently supports both iCloud Drive and iCloud Photos. Backups are taken in a snapshot-like way, meaning that everytime you launch icloudback, a new snapshot folder is created with the current date and all of you iCloud data is scanned with the previous snapshot, if available, to see if there has been any change. If a change is identified, a new version of the file is downloded. If no changes are identified, a hardlink is created to the version already available on your local backup. A convinient `latest` symlink will always point to the latest snapshot folder.

This sofware was inspired by [icloud-docker](https://github.com/mandarons/icloud-docker) and uses [iCloudPy](https://github.com/mandarons/icloudpy) library to communicate with iCloud.

## Installation
There is no docker image available at the moment so you will need to run it manually.

```bash
# Clone the repository
git clone https://github.com/rhaidiz/icloudback

# enter the repository folder
cd icloudback

# create a python venv
python -m venv venv

# install requirements
pip install -r requirements.txt
```

Use your favourite text editor to edit the file config.yaml.

## How to run

To run it (remember to properly configure it first).
```bash
python -m src.main
```

## Configuration sample

```yaml
logger:
  level: DEBUG
  filename: ./icloudback.log

credentials:
  username: email@icloud.com
  password: password_here

root: "/path/to/destination/folder"

# the numebr of threads to use to process your files
threads_count: 5

drive:
  ignore: # Optional - use if you want to exclude something from the backup
    - ".git"
    - ".svn"
    # For folders just type the folder name.
    # No regex supported at the moment.
```
