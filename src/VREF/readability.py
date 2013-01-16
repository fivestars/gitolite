import os
import subprocess
import sys

from readability_checks import language_checks
from ownership_utils import build_commit_to_acceptors_dict, get_files, p


username_to_phid = dict((user['userName'], user['phid']) for user in p.user.query())

oldsha, newsha = sys.argv[1:3]  # oldsha and newsha are passed in as first and second arguments

gl_user = os.environ['GL_USER']
user_phid = (phid for username, phid in username_to_phid.items() if username == gl_user).next()

GET_COMMITS_COMMAND = 'git log --pretty=%H {oldsha}..{newsha}'.format(
        user=gl_user, oldsha=oldsha, newsha=newsha)

CHECK_FAIL_MESSAGE = '''
File {filename} in
{commit_hash}
needs LGTM from someone with readability!
'''
# TODO put in the actual language and list of people with readability
# into this message. Probably requires modifying the language checking class


def check_readability(commit_hashes):
    "Returns False if a file has not been accepted by someone with readability in its language"
    commit_to_acceptors = build_commit_to_acceptors_dict(commit_hashes)

    for commit_hash in commit_hashes:
        files_in_commit = get_files(commit_hash)
        accepted_by = commit_to_acceptors[commit_hash] | set([user_phid])

        for f in files_in_commit:
            if not all(check(f)(accepted_by) for check in language_checks):
                print CHECK_FAIL_MESSAGE.format(filename=f, commit_hash=commit_hash)
                return False

    return True


commit_hashes = subprocess.Popen(GET_COMMITS_COMMAND,
    shell=True, stdout=subprocess.PIPE).stdout.read().split()

if not check_readability(commit_hashes):
    print 'VREF/READABILITY'  # I think this will trigger the rule to fail
