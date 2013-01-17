import os
import subprocess

from base_ownership import BaseReviewCheck
from git_tools import get_files_from_commit, git_readfile


class Ownership(BaseReviewCheck):
    CHECK_FAIL_MESSAGE = '''
    File {filename} in {commit_hash}
    did not receive a LGTM from a code owner!
    Have these guys review your code and try again :(
    {code_owners}
    '''

    FALLTHRU = 'VREF/OWNERSHIP'

    def check(self):
        "Returns False if a modified file has not been accepted by a code owner on Phabricator"
        for commit_hash in self.commit_hashes:
            files_in_commit = get_files_from_commit(commit_hash)
            accepted_by = self.commit_to_acceptors[commit_hash] | set([self.user_phid])

            for f in files_in_commit:
                code_owners = [self.user_to_phid[user] for user in self.get_owners(f)]
                if not (set(accepted_by) & set(code_owners)):
                    self.fallthru(filename=f, commit_hash=commit_hash,
                            code_owners=[self.phid_to_user[owner] for owner in code_owners])
                    return False

        return True

    def get_owners(self, path):
        """Crawls up directory tree to until it finds a .owners file

        Path is relative to top project dir
        Returns None if no .owners file is found
        """
        parent_dir = os.path.dirname(path)
        if not parent_dir:
            return None

        owners_file = git_readfile(os.path.join(parent_dir, '.owners'))
        if owners_file:
            return [line.strip() for line in owners_file.split() if not line.startswith('#')]

        return self.get_owners(parent_dir)


if __name__ == '__main__':
    import sys
    oldsha, newsha = sys.argv[1:3]  # oldsha and newsha are passed in as first and second arguments
    Ownership(oldsha, newsha).check()
