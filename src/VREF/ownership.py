from collections import defaultdict
import os
import subprocess
import sys

from phabricator import Phabricator


p = Phabricator()
username_to_phid = dict((user['userName'], user['phid']) for user in p.user.query())

oldsha, newsha = sys.argv[1:3]  # oldsha and newsha are passed in as first and second arguments

gl_user = os.environ['GL_USER']

# get list of commit hashes (I hope I can do this command even though the code is not merged yet!)
GET_COMMITS_COMMAND = 'git log --pretty=%H {oldsha}..{newsha}'.format(
        user=gl_user, oldsha=oldsha, newsha=newsha)


def check_ownership(commit_hashes):
    commit_to_acceptors = build_commit_to_acceptors_dict(commit_hashes)

    for commit_hash in commit_hashes:
        files_in_commit = get_files(commit_hash)
        accepted_by = commit_to_acceptors[commit_hash]
        for f in files_in_commit:
            code_owners = [username_to_phid[user] for user in read_users_file(find_owners_file(f))]
            if not (set(accepted_by) & set(code_owners)):
                print 'File {} in\n{}\ndid not receive a LGTM from code owner!'.format(
                        f, commit_hash)
                print 'VREF/OWNERSHIP'  # I think this will trigger the rule to fail


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
        users = [line.strip() for line in users_file.readlines() if not line.startswith('#')]
    return users


def find_owners_file(filename):
    "Crawls up directory tree to until it finds a .owners file"
    parent_dir = os.path.dirname(os.path.abspath(filename))
    owners_file = os.path.join(parent_dir, '.owners')
    if os.path.exists(owners_file):
        return owners_file

    return find_owners_file(parent_dir)


commit_hashes = subprocess.call(GET_COMMITS_COMMAND).split('\n')
check_ownership(commit_hashes)
