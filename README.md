# GIT Mass Backup

## Overview
This script is designed to automate the process of backing up and archiving multiple Git repositories, particularly those hosted on GitLab. The repositories are cloned as mirrors to preserve their entire history, compressed into .tar.gz archives for efficient storage, and organized into directories that reflect their group and subgroup hierarchy.

## Use Cases
- **Migrating repositories**: Easily move repositories from one Git version control system to another.
- **Archiving repositories**: Create compressed backups for long-term or offsite storage.
- **Regular backups**: Schedule the script to periodically back up important repositories for disaster recovery.

## Features
- Supports GitLab groups and subgroups for organizing repositories.
- Creates compressed .tar.gz archives of repositories for easier storage and handling.
- Skips repositories that are already archived to save time on retries.
- Automatically cleans up temporary clone directories after compression.

## Requirements
- Python 3.10+ (may work for other versions aswell, I used 3.10.11)
- Dependencies listed in `requirements.txt`

Ensure you have an SSH key configured for Git authentication. The script assumes the SSH key is set up and properly authorized for the repositories being backed up.

## Usage
1. Install dependencies with `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and replace with your credentials and settings
3. Run da script `python main.py`

## Folder Structure

The script preserves the full group and subgroup hierarchy when cloning and archiving repositories. For example:

```text
gitlab_backup/
└── GroupA/
    └── Subgroup1/
        └── AnotherSubgroup2/
            └── Project.git

compressed_backup/
└── GroupA/
    └── Subgroup1/
        └── AnotherSubgroup2/
            └── Project.tar.gz
```

- `gitlab_backup/`: Temporary directory where repositories are cloned as mirrors.
- `compressed_backup/`: Final destination for compressed .tar.gz archives.

After the script completes, the gitlab_backup folder is automatically removed, leaving only the archives.

## Notes and Recommendations
- **Long Execution Time**: Depending on the number and size of repositories, the script may take a significant amount of time to complete.
- **Error Recovery**: Since the script skips repositories that are already archived, you can safely restart it if it fails partway through.
- **Offsite Backups**: Consider storing the generated .tar.gz files in a remote location (e.g., cloud storage, external drives) for better disaster recovery.

## Future Improvements
- Extend support to other Git platforms like GitHub by implementing platform-specific APIs.
- Add an option for incremental backups, only updating archives for repositories with new commits.
- Implement a logging mechanism to track the status of each repository during execution.
- Implement ability to also archive inactive repositories (Adjustable via environment variable)

## License
This project is licensed under the MIT License. See the LICENSE file for details.