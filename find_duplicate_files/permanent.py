def get_archives(cur):
    query = "SELECT archiveId FROM archive WHERE type IS NOT NULL ORDER BY archiveId DESC LIMIT 1000"
    cur.execute(query)
    all_archive_ids = [archiveId[0] for archiveId in cur]
    return all_archive_ids
