from collections import defaultdict
import os
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
            commit_to_acceptors[commit] = commit_to_acceptors[commit] | set(accepted_by)

    return commit_to_acceptors


def get_files(commit_hash):
    "Takes a commit hash and returns a list of files edited in the commit"
    command = 'git show --pretty="format:" --name-only {0}'.format(commit_hash)
    files_altered = subprocess.Popen(command, shell=True,
            stdout=subprocess.PIPE).stdout.read().split()

    return files_altered


def splitpath(path):
    "Splits a path into a list of its individual pieces"
    parts = []
    head, tail = os.path.split(path)
    parts.insert(0, tail)
    while head:
        head, tail = os.path.split(head)
        parts.insert(0, tail)
    return parts


def find_git_hash(ls_tree, name):
    "Takes a list of git ls-tree output and returns hash of desired file/dir if it exists"
    for line in ls_tree:
        if not line:
            continue
        _, git_object, git_hash, filename = line.split()
        if filename == name:
            return git_hash

    return None
