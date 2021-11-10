import logging


def get_archives(cur):
    query = (
        "SELECT archive.archiveId, account.primaryEmail FROM archive "
        "INNER JOIN account_archive ON archive.archiveId = account_archive.archiveId "
        "INNER JOIN account ON account_archive.accountId = account.accountId "
        "WHERE archive.type IS NOT NULL AND archive.status LIKE 'status.generic.ok' "
        "AND account_archive.status like 'status.generic.ok' "
        "AND account_archive.accessRole like 'access.role.owner'"
        "AND account.type LIKE 'type.account.standard' "
        "AND account.primaryEmail NOT LIKE '%@permanent.org' "
        "AND account.createdDT > '2017-01-01 12:00:00' ORDER BY archive.archiveId DESC"
    )
    cur.execute(query)
    all_archives = {}
    for archive_id, email in cur:
        if archive_id in all_archives:
            logging.warn("Error on archive %s, more than one owner.", archive_id)
        all_archives[archive_id] = email
    return all_archives
