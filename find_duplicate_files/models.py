import logging
import collections


class Archive:
    def __init__(self, cur, archive_id, email, name):
        self.cur = cur
        self.archive_id = archive_id
        self.email = email
        self.name = name
        self.duplicate_folder_count = 0
        self.duplicate_file_count = 0
        self.contains_folder_errors = False
        self.contains_record_errors = False
        self.folders = []
        self.files = []

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
        # Get all valid folders associated with an archive
        query = (
            "SELECT folder.folderId, folder.displayName, folder.type, folder.status, folder_link.parentFolderId "
            "FROM folder INNER JOIN folder_link ON folder.folderId = folder_link.folderId "
            "WHERE folder.archiveId = %s AND folder_link.archiveId = %s AND folder.type NOT IN "
            "('type.folder.vault', 'type.folder.root.vault', 'type.folder.root.share') "
            "AND folder.status NOT LIKE 'status.generic.deleted' AND "
            "folder_link.type NOT IN "
            "('type.folder_link.root.share', 'type.folder_link.share', 'type.folder_link.vault') "
            "AND folder_link.status NOT LIKE 'status.generic.deleted'"
        )

        self.cur.execute(query, (self.archive_id, self.archive_id))
        folders = {}
        for (
            folder_id,
            display_name,
            folder_type,
            folder_status,
            parent_folder_id,
        ) in self.cur:
            if folder_id not in folders:
                folders[folder_id] = Folder(
                    folder_id,
                    display_name,
                    folder_type,
                    folder_status,
                    parent_folder_id,
                )
            else:
                folders[folder_id].parent_folders.append(parent_folder_id)

        # Build directory hierarchy
        self.recursively_organize_folder_paths(folders)

        self.fetch_file_paths(folders)

        # Identify archives with duplicate folders
        if len(self.folders) != len(set(self.folders)):
            logging.debug(
                "Duplicates folders found for archive %s %s",
                self.archive_id,
                self.email,
            )
            duplicates = [
                f"{item} [{count}]"
                for item, count in collections.Counter(self.folders).items()
                if count > 1
            ]
            logging.debug("\n\t-%s", "\n\t-".join(duplicates))
            self.duplicate_folder_count = len(duplicates)

        # Identify archives with duplicate file paths
        if len(self.files) != len(set(self.files)):
            logging.debug(
                "Duplicates files for archive %s %s", self.archive_id, self.email
            )
            duplicates = [
                f"{item} [{count}]"
                for item, count in collections.Counter(self.files).items()
                if count > 1
            ]
            logging.debug("\n\t-%s", "\n\t-".join(duplicates))
            self.duplicate_file_count = len(duplicates)

    def recursively_organize_folder_paths(self, folders):
        for folder_id, folder in folders.items():
            path = "/" + folder.name
            if folder.parent_folders == []:  # This is the Archive root
                self.folders.append(path)
            else:
                for parent_id in folder.parent_folders:
                    current_parent = parent_id
                    while current_parent:
                        if current_parent not in folders:
                            # Usually this means that the parent was deleted
                            logging.debug(
                                "Error, missing parent_id %d for folder %d in archive %d.",
                                current_parent,
                                folder_id,
                                self.archive_id,
                            )
                            current_parent = None
                            self.contains_folder_errors = True
                            path = None
                        else:
                            parent = folders[current_parent]
                            path = "/" + parent.name + path
                            current_parent = (
                                parent.parent_folders[0]
                                if len(parent.parent_folders)
                                else None
                            )
                    if path:
                        self.folders.append(path)
                        folders[folder_id].paths.append(path)
                        path = "/" + folder.name

    def fetch_file_paths(self, folders):
        # Get all valid records associated with an archive
        query = (
            "SELECT record.recordId, record.displayName, record.status, folder_link.parentFolderId "
            "FROM record INNER JOIN folder_link ON record.recordId = folder_link.recordId "
            "WHERE record.archiveId = %s AND folder_link.archiveId = %s AND record.type NOT IN "
            "('type.folder.vault', 'type.folder.root.vault', 'type.folder.root.share') "
            "AND record.status NOT IN ('status.generic.error', 'status.generic.deleted') AND "
            "folder_link.type NOT IN "
            "('type.folder_link.root.share', 'type.folder_link.share', 'type.folder_link.vault') "
            "AND folder_link.status NOT LIKE 'status.generic.deleted'"
        )

        self.cur.execute(query, (self.archive_id, self.archive_id))

        for (
            record_id,
            display_name,
            record_status,
            parent_folder_id,
        ) in self.cur:
            if parent_folder_id not in folders:
                # Parent folder was probably deleted
                logging.debug(
                    "Unknown parent folder %s for record %s (%s) in archive %s",
                    parent_folder_id,
                    record_id,
                    record_status,
                    self.archive_id,
                )
                self.contains_record_errors = True
            else:
                for path in folders[parent_folder_id].paths:
                    self.files.append(path + "/" + display_name)


class Folder:
    def __init__(self, fid, name, ftype, status, parent_folder_id=None):
        self.id = fid
        self.name = name
        self.paths = []
        self.type = ftype
        self.status = status
        self.parent_folders = []
        if parent_folder_id:
            self.parent_folders.append(parent_folder_id)
