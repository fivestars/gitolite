from collections import defaultdict
import os
import subprocess
import sys

from phabricator import Phabricator


def get_files_from_commit(commit_hash):
    "Takes a commit hash and returns a list of files edited in the commit"
    cmd = 'git show --pretty="format:" --name-only {0}'.format(commit_hash)
    files_altered = subprocess.Popen(cmd, shell=True,
            stdout=subprocess.PIPE).stdout.read().split()

    return files_altered


def splitpath(path):
    "Splits a path into a list of its individual pieces"
    parts = []
    while path:
        path, tail = os.path.split(path)
        parts.insert(0, tail)
    return parts


def find_git_hash(ls_tree, name):
    "Takes a git ls-tree output in list form and returns hash of desired file/dir if it exists"
    for line in ls_tree:
        if not line:
            continue
        _, _, git_hash, filename = line.split()
        if filename == name:
            return git_hash

    return None


class BaseReviewCheck:
    p = Phabricator()

    gl_user = os.environ['GL_USER']

    GET_COMMITS_COMMAND = 'git log --pretty=%H {oldsha}..{newsha}'

    def __init__(self, oldsha, newsha):
        self.oldsha = oldsha
        self.newsha = newsha
        self.commit_hashes = subprocess.Popen(
                self.GET_COMMITS_COMMAND.format(oldsha=oldsha, newsha=newsha),
                shell=True,
                stdout=subprocess.PIPE).stdout.read().split()

        self.user_to_phid = dict((user['userName'], user['phid']) for user in self.p.user.query())
        self.phid_to_user = dict((phid, user) for user, phid in self.user_to_phid.items())

        self.user_phid = self.user_to_phid[self.gl_user]

        self.commit_to_acceptors = self.build_commit_to_acceptors_dict()

    def build_commit_to_acceptors_dict(self):
        "Return a dictionary of commit -> set of PHIDs that gave it a LGTM on Phabricator"
        diffs = self.p.differential.query(commitHashes=[['gtcm', sha] for sha in self.commit_hashes],
                status='status-open')

        revisions_involved = [diff['id'] for diff in diffs]
        revision_to_comments = self.p.differential.getrevisioncomments(ids=revisions_involved)

        commit_to_acceptors = defaultdict(set)

        for diff in diffs:
            revision_id = int(diff['id'])
            comments = revision_to_comments[str(revision_id)]

            accepted_by = [comment['authorPHID'] for comment in comments \
                                                 if 'LGTM' in comment['content']]

            commits_in_revision = [sha for hash_type, sha in diff['hashes'] if hash_type == 'gtcm']

            for commit in commits_in_revision:
                commit_to_acceptors[commit] = commit_to_acceptors[commit] | set(accepted_by)

        return commit_to_acceptors

    def fallthru(self, **kwargs):
        print self.CHECK_FAIL_MESSAGE.format(**kwargs)
        print self.FALLTHRU
