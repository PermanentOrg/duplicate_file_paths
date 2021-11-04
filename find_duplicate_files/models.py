import logging


class Archive:
    def __init__(self, cur, archive_id):
        self.cur = cur
        self.archive_id = archive_id

    def get_duplicated_paths(self):
        """
        Folder types included in the below query:
         - type.folder.app
         - type.folder.private
         - type.folder.public
         - type.folder.root.app
         - type.folder.root.private
         - type.folder.root.public
         - type.folder.root.root

        Folder types excluded because deprecated:
         - type.folder.vault
         - type.folder.root.vault
         - type.folder_link.vault

        Folder types excluded because they belong to a different archive:
         - type.folder.root.share
         - type.folder_link.root.share
         - type.folder_link.share
        """

        # logging.debug("Finding dupe paths for archive %d", self.archive_id)
        query = (
            "SELECT folder.folderId, folder.displayName, folder.type, "
            "folder_link.parentFolderId FROM folder "
            "INNER JOIN folder_link ON folder.folderId = folder_link.folderId "
            "WHERE folder.archiveId = %s AND folder.type NOT IN "
            "('type.folder.vault', 'type.folder.root.vault', 'type.folder.root.share') "
            "AND folder_link.type NOT IN "
            "('type.folder_link.root.share', 'type.folder_link.share', 'type.folder_link.vault')"
        )

        self.cur.execute(query, (self.archive_id,))
        folders = {}
        for folder_id, display_name, folder_type, parent_folder_id in self.cur:
            folders[folder_id] = {
                "name": display_name,
                "type": folder_type,
                "parent_id": parent_folder_id,
            }

        folders_with_paths = self.recursively_organize_folder_paths(folders)

        return False

    def recursively_organize_folder_paths(self, folders):
        folders_with_paths = {}
        for folder_id, values in folders.items():
            parent_id = values["parent_id"]
            path = "/" + values["name"]
            if parent_id:
                while parent_id:
                    if parent_id not in folders:
                        logging.debug(
                            "Error, missing parent_id %d in archive: %d",
                            parent_id,
                            self.archive_id,
                        )
                        parent_id = None
                    else:
                        parent = folders[parent_id]
                        path = "/" + parent["name"] + path
                        parent_id = parent["parent_id"]
            folders_with_paths[folder_id] = {"type": values["type"], "path": path}
        return folders_with_paths
