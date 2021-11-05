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
    logging.getLogger().setLevel(logging.DEBUG)
    all_archives = get_archives(cur)
    for archive_id, email in all_archives.items():
        Archive(cur, archive_id, email).get_duplicated_paths()


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
