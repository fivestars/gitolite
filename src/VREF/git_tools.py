import os
import subprocess


def get_files_from_commit(commit_hash):
    "Takes a commit hash and returns a list of files edited in the commit"
    cmd = 'git show --pretty="format:" --name-only {0}'.format(commit_hash)
    files_altered = subprocess.Popen(cmd, shell=True,
            stdout=subprocess.PIPE).stdout.read().split()

    return files_altered


def git_readfile(path, commit_hash=None):
    """Reads a file using git for a given commit hash, or HEAD

    Returns None if file doesnt exist
    """
    return subprocess.Popen(
            'git cat-file -p {git_hash}:{path}'.format(git_hash=commit_hash or 'HEAD', path=path),
            shell=True,
            stdout=subprocess.PIPE).stdout.read()
