import logging


class Archive:
    def __init__(self, cur, archive_id):
        self.cur = cur
        self.archive_id = archive_id

    def get_duplicated_paths(self):
        logging.debug("Finding dupe paths for %d" % self.archive_id)

        query = (
            "SELECT folder.folderId, folder.displayName, folder.type, "
            "folder_link.parentFolderId FROM folder INNER JOIN folder_link ON "
            "folder.folderId = folder_link.folderId WHERE folder.archiveId = %s"
        )

        self.cur.execute(query, (self.archive_id,))
        for folder_id, display_name, folder_type, parent_folder_id in self.cur:
            logging.debug("Found %s" % display_name)

        return False
