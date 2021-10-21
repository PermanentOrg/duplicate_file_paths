# Duplicate File Paths

This script is used to identify the number of duplicate file paths within a particular archive. Permanent.org allows duplicate file paths, but this is quite non-standard, and causes problems for pretty much every other service or tool that emulates a filesystem.

## Run

This script requires access to a Permanent database. Since the databases are not publically routable, this script must be run directly on a server that has DB access.

First, install a mysql-client library.
```
apt-get install mysql-client
```

Then, set up a virtual environment and install the project requirements.
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Finally, run the script.
```
python3 -m find_duplicate_files <user> <password> <host> <database>
```
