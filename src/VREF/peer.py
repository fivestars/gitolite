import os
import subprocess
import sys

from ownership_utils import build_commit_to_acceptors_dict, p


oldsha, newsha = sys.argv[1:3]  # oldsha and newsha are passed in as first and second arguments

gl_user = os.environ['GL_USER']
user_phid = p.user.query(usernames=[gl_user])[0]['phid']

GET_COMMITS_COMMAND = 'git log --pretty=%H {oldsha}..{newsha}'.format(
        user=gl_user, oldsha=oldsha, newsha=newsha)

CHECK_FAIL_MESSAGE = '''
Commit {commit_hash}
did not get an LGTM from a peer.
Have someone look at it and then we can talk.
'''


def check_peer(commit_hashes):
    "Returns False if a commit has not been accepted on Phabricator by not the pusher"
    commit_to_acceptors = build_commit_to_acceptors_dict(commit_hashes)

    for commit_hash in commit_hashes:
        if not (commit_to_acceptors[commit_hash] - set([gl_user])):
            print CHECK_FAIL_MESSAGE.format(commit_hash=commit_hash)
            return False

    return True


commit_hashes = subprocess.call(GET_COMMITS_COMMAND).split()

if not check_peer(commit_hashes):
    print 'VREF/PEER'
