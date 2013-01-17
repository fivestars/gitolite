from base_ownership import BaseReviewCheck
from git_tools import get_files_from_commit
from readability_checkers import language_checkers


class Readability(BaseReviewCheck):
    CHECK_FAIL_MESSAGE = '''
    File {filename} in
    {commit_hash}
    needs LGTM from someone with {language} readability!
    Get one of these people to review it:
    {readability}
    '''

    FALLTHRU = 'VREF/READABILITY'

    def __init__(self, oldsha, newsha, language_checkers):
        super(Readability, self).__init__(oldsha, newsha)
        self.language_checkers = language_checkers

    def check(self):
        "Returns False if a file has not been accepted by someone with readability in its language"
        for commit_hash in self.commit_hashes:
            files_in_commit = get_files_from_commit(commit_hash)
            accepted_by = self.commit_to_acceptors[commit_hash] | set([self.user_phid])

            for f in files_in_commit:
                for language, checker, in self.language_checkers.items():

                    # should meet readability conditions at last commit, aka newsha
                    language_checker = checker(self.newsha, f)
                    accepting_users = [self.phid_to_user[phid] for phid in accepted_by]

                    if language_checker.match() and not language_checker.accepted(accepting_users):
                        self.fallthru(filename=f, commit_hash=commit_hash, language=language,
                                readability=language_checker.readability)
                        return False

        return True


if __name__ == '__main__':
    import sys
    oldsha, newsha = sys.argv[1:3]  # oldsha and newsha are passed in as first and second arguments
    Readability(oldsha, newsha, language_checkers).check()
