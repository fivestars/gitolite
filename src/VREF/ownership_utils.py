from collections import defaultdict
import subprocess

from phabricator import Phabricator


p = Phabricator()


def build_commit_to_acceptors_dict(commit_hashes):
    "Returns a dictionary of commit -> set of PHIDS that have given it a LGTM on Phabricator"
    diffs = p.differential.query(
            commitHashes=[['gtcm', sha] for sha in commit_hashes],
            status='status-open')

    commit_to_acceptors = defaultdict(set)

    for diff in diffs:
        revision_id = int(diff['id'])
        commits_in_revision = [pair[1] for pair in diff['hashes'] if pair[0] == 'gtcm']

        accepted_by = [comment['authorPHID'] for comment in comments \
                                             if 'LGTM' in comment['content']]

        for commit in commits_in_revision:
            commit_to_acceptors.union(accepted_by)

    return commit_to_acceptors


def get_files(commit_hash):
    "Takes a commit hash and returns a list of files edited in the commit"
    command = 'git show --pretty="format:" --name-only {0}'.format(commit_hash)
    files_altered = subprocess.call(command).split()

    return files_altered


def read_users_file(path):
    "Reads a .owners or readability file with usernames separated by whitespace/newlines"
    with open(path) as users_file:
        users = [line.strip().strip('*') for line in users_file.readlines() if not line.startswith('#')]
    return users
