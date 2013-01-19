from collections import defaultdict
import os
import subprocess
import sys

from git import Repo
from phabricator import Phabricator


class BaseVREF(object):
    def __init__(self, oldsha, newsha, repo_path):
        self.gl_user = os.environ['GL_USER']

        self.oldsha = oldsha
        self.newsha = newsha
        self.repo = Repo(repo_path)

        self.commit_hashes = self.get_all_commits(oldsha, newsha)

    def fallthru(self, **kwargs):
        "Prints failure message and VREF fallthru text"
        print self.CHECK_FAIL_MESSAGE.format(**kwargs)
        print self.FALLTHRU

    def get_files_in_commit(self, commit_hash):
        return self.repo.git.show('--pretty=format:', '--name-only', commit_hash).split()

    def read_git_file(self, path, commit='HEAD'):
        return self.repo.git.cat_file('-p', commit + ':' + path)

    def get_all_commits(self, oldsha, newsha):
        commits = self.repo.commit(newsha).iter_parents()
        next_commit = commits.next()

        commit_hashes = [newsha]
        while next_commit.hexsha != oldsha:
            commit_hashes.append(next_commit.hexsha)
            next_commit = commits.next()

        return commit_hashes


class BaseReviewCheck(BaseVREF):
    p = Phabricator()

    def __init__(self, oldsha, newsha, repo_path):
        super(BaseReviewCheck, self).__init__(oldsha, newsha, repo_path)

        self.phid_to_user = dict((user['phid'], user['userName']) for user in self.p.user.query())

        self.commit_to_acceptors = self.build_commit_to_acceptors_dict()

    def build_commit_to_acceptors_dict(self):
        "Return a dictionary of commit -> set of usernames that gave it a LGTM on Phabricator"
        diffs = self.p.differential.query(
                commitHashes=[['gtcm', sha] for sha in self.commit_hashes],
                status='status-open')

        revisions_involved = [diff['id'] for diff in diffs]
        revision_to_comments = self.p.differential.getrevisioncomments(ids=revisions_involved)

        commit_to_acceptors = defaultdict(set)

        for diff in diffs:
            revision_id = int(diff['id'])
            comments = revision_to_comments[str(revision_id)]

            accepted_by = [self.phid_to_user[comment['authorPHID']] for comment in comments \
                                                                    if 'LGTM' in comment['content']]

            commits_in_revision = [sha for hash_type, sha in diff['hashes'] if hash_type == 'gtcm']

            for commit in commits_in_revision:
                commit_to_acceptors[commit] = commit_to_acceptors[commit] | set(accepted_by)

        return commit_to_acceptors
