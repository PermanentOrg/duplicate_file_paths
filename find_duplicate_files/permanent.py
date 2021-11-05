def get_archives(cur):
    query = (
        "SELECT archive.archiveId, account.primaryEmail FROM archive "
        "INNER JOIN account_archive ON archive.archiveId = account_archive.archiveId "
        "INNER JOIN account ON account_archive.accountId = account.accountId "
        "WHERE archive.type IS NOT NULL AND archive.status LIKE 'status.generic.ok' "
        "ORDER BY archive.archiveId DESC LIMIT 620"  # TODO: Remove limit when running on prod
    )
    cur.execute(query)
    all_archives = {}
    for account_id, email in cur:
        all_archives[account_id] = email
    return all_archives
