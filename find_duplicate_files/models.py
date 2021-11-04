import logging
import collections


class Archive:
    def __init__(self, cur, archive_id):
        self.cur = cur
        self.archive_id = archive_id
        self.folders = []

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

        Folder statuses excluded:
         - status.generic.deleted
        """

        # logging.debug("Finding dupe paths for archive %d", self.archive_id)
        query = (
            "SELECT folderId, displayName, type, status "
            "FROM folder WHERE archiveId = %s AND folder.type NOT IN "
            "('type.folder.vault', 'type.folder.root.vault', 'type.folder.root.share') "
            "AND status NOT LIKE 'status.generic.deleted'"
        )

        self.cur.execute(query, (self.archive_id,))
        folders = {}
        for (
            folder_id,
            display_name,
            folder_type,
            folder_status,
        ) in self.cur:
            folders[folder_id] = {
                "name": display_name,
                "type": folder_type,
                "status": folder_status,
                "parent_folders": [],
            }

        for folder in folders:
            query = (
                "SELECT parentFolderId FROM folder_link WHERE folderId = %s "
                "AND archiveId = %s AND type NOT IN "
                "('type.folder_link.root.share', 'type.folder_link.share', 'type.folder_link.vault') "
                "AND status NOT LIKE 'status.generic.deleted'"
            )
            self.cur.execute(query, (folder, self.archive_id))
            for (parent_folder_id,) in self.cur:
                folders[folder]["parent_folders"].append(parent_folder_id)

        self.recursively_organize_folder_paths(folders)

        if len(self.folders) != len(set(self.folders)):
            logging.debug(self.archive_id)
            print([item for item, count in collections.Counter(self.folders).items() if count > 1])

        return False

    def recursively_organize_folder_paths(self, folders):
        folders_with_paths = {}
        for folder_id, values in folders.items():
            parent_ids = values["parent_folders"]
            path = "/" + values["name"]
            if parent_ids == []:  # This is the Archive root
                folders_with_paths[folder_id] = {
                    "type": values["type"],
                    "path": path,
                }
                self.folders.append(path)
            else:
                for parent_id in parent_ids:
                    current_parent = parent_id
                    while current_parent:
                        if current_parent not in folders:
                            logging.debug(
                                "Error, missing parent_id %d for folder %d in archive %d.",
                                current_parent,
                                folder_id,
                                self.archive_id,
                            )
                            current_parent = None
                        else:
                            parent = folders[current_parent]
                            path = "/" + parent["name"] + path
                            current_parent = parent["parent_folders"][0] if len(parent["parent_folders"]) else None

                    folders_with_paths[folder_id] = {
                        "type": values["type"],
                        "path": path,
                    }
                    self.folders.append(path)

        return folders_with_paths
