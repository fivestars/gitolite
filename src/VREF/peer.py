from base_ownership import BaseReviewCheck


class Peer(BaseReviewCheck):
    CHECK_FAIL_MESSAGE = '''
    Commit {commit_hash}
    did not get an LGTM from a peer.
    Have someone look at it and then we can talk.
    '''

    FALLTHRU = 'VREF/PEER'

    def check(self):
        "Returns False if a commit has not been accepted on Phabricator by not the pusher"
        for commit_hash in self.commit_hashes:
            if not (self.commit_to_acceptors[commit_hash] - set([self.user_phid])):
                self.fallthru(commit_hash=commit_hash)
                return False

        return True


if __name__ == '__main__':
    import sys
    oldsha, newsha = sys.argv[1:3]  # oldsha and newsha are passed in as first and second arguments
    Peer(oldsha, newsha).check()
