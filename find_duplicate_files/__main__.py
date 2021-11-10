#!/usr/bin/env python3

import argparse
import logging
from collections import defaultdict

import mysql.connector

from .utils import get_archives
from .models import Archive


def parse_args():
    parser = argparse.ArgumentParser(
        description="Find duplicate filepaths within an archive",
    )
    parser.add_argument(
        "user",
        help="The database user",
    )
    parser.add_argument(
        "password",
        help="The database user's password",
    )
    parser.add_argument(
        "host",
        help="The database host",
    )
    parser.add_argument(
        "database",
        help="The database name",
    )

    return parser.parse_args()


def main(cur):
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    all_archives = get_archives(cur)

    logging.info("%s total archives", len(all_archives))

    statistics = {
        "archives_with_duplicated_folders": 0,
        "archives_with_folder_errors": 0,
        "archives_with_duplicated_files": 0,
        "archives_with_file_errors": 0,
    }
    archive_info = defaultdict(dict)
    for archive_id, email in all_archives.items():
        a = Archive(cur, archive_id, email)
        a.get_duplicated_paths()
        if a.duplicate_folder_count:
            statistics["archives_with_duplicated_folders"] += 1
            archive_info[archive_id]["email"] = a.email
            archive_info[archive_id][
                "duplicated_folder_count"
            ] = a.duplicate_folder_count
        if a.contains_folder_errors:
            statistics["archives_with_folder_errors"] += 1
        if a.duplicate_file_count:
            statistics["archives_with_duplicated_files"] += 1
            archive_info[archive_id]["email"] = a.email
            archive_info[archive_id]["duplicated_file_count"] = a.duplicate_file_count
        if a.contains_record_errors:
            statistics["archives_with_file_errors"] += 1

    logging.info(statistics)
    for archive_id, info in archive_info.items():
        print(
            archive_id,
            info["email"],
            info.get("duplicated_folder_count"),
            info.get("duplicated_file_count"),
        )


if __name__ == "__main__":
    args = parse_args()
    try:
        cnx = mysql.connector.connect(
            user=args.user,
            password=args.password,
            host=args.host,
            database=args.database,
        )
    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            logging.error("Something is wrong with your user name or password")
        elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            logging.error("Database does not exist")
        else:
            logging.error(err)

    cursor = cnx.cursor()
    main(cursor)
    cursor.close()
    cnx.close()
