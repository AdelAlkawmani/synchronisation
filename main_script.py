import filecmp
import sys
import os
import shutil


# ِCommand line arguments
path1 = sys.argv[1]
path2 = sys.argv[2]
path_log = os.path.join(sys.argv[3], 'Log.txt')


class Archive:

    def __init__(self):
        self.pathways_list = []
        self.copied_files = 0
        self.copied_folders = 0

    def to_add_pathway(self, pathway):
        self.pathways_list.append(pathway)

    def to_control_pathways(self):
        pathways_count = len(self.pathways_list)
        for pathway in self.pathways_list:
            if self.pathways_list.index(pathway) < pathways_count - 1:
                pathway_2 = self.pathways_list[self.pathways_list.index(pathway) + 1]
                record = "Target files for synchronization: source and archive has been controlled"
                print(record)
                to_save_log(record)
                self.to_compare_dirs(pathway.root_path, pathway_2.root_path)

    def to_compare_dirs(self, archive, source):
        comparsion = filecmp.dircmp(archive, source)
        updated_archive = []
        updated_source = []

        # Case: folders are in common
        if comparsion.common_dirs:
            for d in comparsion.common_dirs:
                self.to_compare_dirs(os.path.join(archive, d), os.path.join(source, d))
        if comparsion.right_only:
            self.to_copy(comparsion.right_only, source, archive)
        if comparsion.left_only:
            self.to_copy(comparsion.left_only, archive, source)

        # Case: Update uncommon folders
        if comparsion.diff_files:
            for d in comparsion.diff_files:
                archive_modifications = os.stat(os.path.join(archive, d)).st_mtime
                source_modifications = os.stat(os.path.join(source, d)).st_mtime
                if archive_modifications > source_modifications:
                    updated_archive.append(d)
                else:
                    updated_source.append(d)
        self.to_copy(updated_archive, archive, source)
        self.to_copy(updated_source, source, archive)

    def to_copy(self, files_list, source, archive):
        for f in files_list:
            source_path = os.path.join(source, os.path.basename(f))
            # Folders synchronization
            if os.path.isdir(source_path):
                shutil.copytree(source_path, os.path.join(archive, os.path.basename(f)))
                self.copied_folders += 1
                record = f"The directory\" {os.path.basename(source_path)} \"  as been copied from \"{os.path.dirname(source_path)}\" to \"{archive}\""
                print(record)
                to_save_log(record)
            # Files synchronization
            else:
                shutil.copy2(source_path, archive)
                self.copied_files += 1
                record = f"The \" {os.path.basename(source_path)} \"  has been copies from \"{os.path.dirname(source_path)}\" to \"{archive}\""
                print(record)
                to_save_log(record)


class Pathway:

    def __init__(self, path, name: str):
        self.name = name
        self.root_path = os.path.abspath(path)
        self.files_list = os.listdir(self.root_path)


def to_save_log(st: str):
    try:
        with open(path_log, 'a+') as log:
            log.write(st + '\n' + '\n')
    except (OSError, IOError) as e:
        print(str(e))
    finally:
        log.close()


if __name__ == "__main__":
    new_archive = Archive()
    pathway_1 = Pathway(path1, "source")
    pathway_2 = Pathway(path2, "archive")
    new_archive.to_add_pathway(pathway_1)
    new_archive.to_add_pathway(pathway_2)
    new_archive.to_control_pathways()
    record_1 = "[{0}] is total number of copied files".format(str(new_archive.copied_files))
    record_2 = "[{0}] is total number of copied folders".format(str(new_archive.copied_folders))
    print(record_1)
    print(record_2)
    to_save_log(record_1)
    to_save_log(record_2)
