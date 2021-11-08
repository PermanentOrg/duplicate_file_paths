#!/usr/bin/env python3

import argparse
import logging

import mysql.connector

from .permanent import get_archives
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
    archive_count = len(all_archives)
    archives_with_dupes = 0
    archives_with_errors = 0
    for archive_id, email in all_archives.items():
        a = Archive(cur, archive_id, email)
        a.get_duplicated_paths()
        if a.duplicates_found:
            archives_with_dupes += 1
        if a.contains_errors:
            archives_with_errors += 1
    logging.info(
        "Out of %s archives, %s have duplicate folders, %s have errors",
        archive_count,
        archives_with_dupes,
        archives_with_errors,
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
