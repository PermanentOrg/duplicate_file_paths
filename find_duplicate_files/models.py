import logging


class Archive:
    def __init__(self, cur, archive_id):
        self.cur = cur
        self.archive_id = archive_id

    def get_duplicated_paths(self):
        logging.debug("Finding dupe paths for %d" % self.archive_id)
        query = "SELECT displayName, folderId FROM folder WHERE archiveId = %s"
        self.cur.execute(query, (self.archive_id,))
        for displayName, folderId in self.cur:
            logging.debug("Found %s" % displayName)
        return False
