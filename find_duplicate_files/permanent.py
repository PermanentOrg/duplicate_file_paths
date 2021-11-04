def get_archives(cur):
    query = "SELECT archiveId FROM archive WHERE type IS NOT NULL ORDER BY archiveId DESC LIMIT 10"
    cur.execute(query)
    return [archiveId[0] for archiveId in cur]
