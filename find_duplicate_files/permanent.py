def get_archives(cur):
    query = "SELECT archiveId FROM archive LIMIT 1000"
    cur.execute(query)
    return [archiveId[0] for archiveId in cur]
