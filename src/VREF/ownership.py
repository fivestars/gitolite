import subprocess

from base_ownership import BaseReviewCheck, get_files_from_commit, splitpath, find_git_hash


class Ownership(BaseReviewCheck):
    CHECK_FAIL_MESSAGE = '''
    File {filename} in {commit_hash}
    did not receive a LGTM from a code owner!
    Try one of:
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

        path is relative to top project dir"""
        owners_hash = ''
        next_dir = ''
        path_parts = splitpath(path)

        for i in range(len(path_parts)):
            ls_tree = subprocess.Popen(
                    'git ls-tree {git_hash}'.format(git_hash=(next_dir or self.oldsha)),
                    shell=True,
                    stdout=subprocess.PIPE).stdout.read().split('\n')

            owners_hash = find_git_hash(ls_tree, '.owners') or owners_hash
            next_dir = find_git_hash(ls_tree, path_parts[i])

        owners_file = subprocess.Popen(
                'git cat-file -p {git_hash}'.format(git_hash=owners_hash),
                shell=True,
                stdout=subprocess.PIPE).stdout.read()

        owners = [line.strip() for line in owners_file.split() if not line.startswith('#')]

        return owners


if __name__ == '__main__':
    import sys
    oldsha, newsha = sys.argv[1:3]  # oldsha and newsha are passed in as first and second arguments
    Ownership(oldsha, newsha).check()
