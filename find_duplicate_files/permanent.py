def get_archives(cur):
    query = "SELECT archiveId FROM archive"
    cursor.execute(query)
    return [archiveId for archiveId in cursor]
