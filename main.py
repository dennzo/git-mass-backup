import os
import subprocess
import requests
import tarfile
import stat
import shutil

from dotenv import load_dotenv

load_dotenv()

# Prepare Configuration
GITLAB_API_URL = str(os.getenv('GITLAB_API_URL')) # Yeah, well the GitLab api base url
PRIVATE_TOKEN = str(os.getenv('GITLAB_PAT'))  # Replace with your GitLab personal access token
INCLUDE_GROUPS = list(os.getenv('INCLUDE_GROUPS').split(',')) # Groups that should be included
TEMPORARY_BACKUP_DIR = str(os.getenv('TEMPORARY_BACKUP_DIR'))  # Temporary directory for cloning repositories
ARCHIVE_DIR = str(os.getenv('ARCHIVE_DIR'))  # Final directory for compressed backups



# Functions
def get_group_projects(group_id):
    """Retrieve all projects within a group (including subgroups)."""
    projects = []
    page = 1
    while True:
        response = requests.get(
            f"{GITLAB_API_URL}/groups/{group_id}/projects",
            headers={"PRIVATE-TOKEN": PRIVATE_TOKEN},
            params={"per_page": 100, "page": page, "include_subgroups": "true"}
        )
        response.raise_for_status()
        data = response.json()
        if not data:
            break
        projects.extend(data)
        page += 1
    return projects

def get_groups():
    """Retrieve all groups the user has access to."""
    groups = []
    page = 1
    while True:
        response = requests.get(
            f"{GITLAB_API_URL}/groups",
            headers={"PRIVATE-TOKEN": PRIVATE_TOKEN},
            params={"per_page": 100, "page": page}
        )
        response.raise_for_status()
        data = response.json()
        if not data:
            break
        groups.extend(data)
        page += 1
    return groups

def mirror_clone(repo_url, destination):
    """Clone the repository as a mirror."""
    subprocess.run(
        ["git", "clone", "--mirror", repo_url, destination],
        check=True
    )

def compress_directory(source_dir, output_file):
    """Compress a directory into a .tar.gz archive."""
    with tarfile.open(output_file, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))
    print(f"Compressed {source_dir} -> {output_file}")

def cleanup_directory(directory):
    """Remove a directory and all its contents, handling read-only files."""
    def remove_readonly(func, path, exc_info):
        # Remove read-only attribute and retry
        os.chmod(path, stat.S_IWRITE)
        func(path)

    shutil.rmtree(directory, onerror=remove_readonly)
    print(f"Deleted directory: {directory}")

def ensure_directories_exist(path):
    """Ensure all directories in the given path exist."""
    os.makedirs(path, exist_ok=True)

def backup_projects():
    """Main function to back up selected groups and their projects."""
    all_groups = get_groups()

    for group in all_groups:
        if group["name"] in INCLUDE_GROUPS:
            print(f"Processing group: {group['name']}")
            projects = get_group_projects(group["id"])

            for project in projects:
                # Construct the full path for subgroups
                project_path = project["path_with_namespace"]  # Full namespace path (e.g., "GroupA/Subgroup1/Project")
                project_clone_path = os.path.join(TEMPORARY_BACKUP_DIR, f"{project_path}.git")
                archive_file_path = os.path.join(ARCHIVE_DIR, f"{project_path}.tar.gz")

                # Ensure the subgroup structure exists
                ensure_directories_exist(os.path.dirname(project_clone_path))
                ensure_directories_exist(os.path.dirname(archive_file_path))

                # Skip if archive already exists
                if os.path.exists(archive_file_path):
                    print(f"Skipping existing archive: {archive_file_path}")
                    continue

                # Clone repository
                print(f"Cloning project: {project['name']} -> {project_clone_path}")
                mirror_clone(project["ssh_url_to_repo"], project_clone_path)

                # Compress repository
                print(f"Compressing project: {project_clone_path} -> {archive_file_path}")
                compress_directory(project_clone_path, archive_file_path)

                # Cleanup uncompressed clone
                cleanup_directory(project_clone_path)

    # Cleanup the main backup directory after processing all groups
    if os.path.exists(TEMPORARY_BACKUP_DIR):
        print(f"Removing main backup directory: {TEMPORARY_BACKUP_DIR}")
        cleanup_directory(TEMPORARY_BACKUP_DIR)

# Main script execution
if __name__ == "__main__":
    ensure_directories_exist(TEMPORARY_BACKUP_DIR)
    ensure_directories_exist(ARCHIVE_DIR)
    backup_projects()
