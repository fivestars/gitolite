import os
import subprocess
import sys

from ownership_utils import build_commit_to_acceptors_dict, get_files, read_users_file, p


username_to_phid = dict((user['userName'], user['phid']) for user in p.user.query())

oldsha, newsha = sys.argv[1:3]  # oldsha and newsha are passed in as first and second arguments

gl_user = os.environ['GL_USER']

# get list of commit hashes (I hope I can do this command even though the code is not merged yet!)
GET_COMMITS_COMMAND = 'git log --pretty=%H {oldsha}..{newsha}'.format(
        user=gl_user, oldsha=oldsha, newsha=newsha)

CHECK_FAIL_MESSAGE = '''
File {filename} in
{commit_hash}
did not receive a LGTM from code owner!
'''


def check_ownership(commit_hashes):
    "Returns False if a modified file has not been accepted by a code owner on Phabricator"
    commit_to_acceptors = build_commit_to_acceptors_dict(commit_hashes)

    for commit_hash in commit_hashes:
        files_in_commit = get_files(commit_hash)
        accepted_by = commit_to_acceptors[commit_hash]

        for f in files_in_commit:
            code_owners = [username_to_phid[user] for user in read_users_file(find_owners_file(f))]
            if not (set(accepted_by) & set(code_owners)):
                print CHECK_FAIL_MESSAGE.format(dict(filename=f, commit_hash=commit_hash))
                return False

    return True


def find_owners_file(filename):
    "Crawls up directory tree to until it finds a .owners file"
    parent_dir = os.path.dirname(os.path.abspath(filename))
    owners_file = os.path.join(parent_dir, '.owners')
    if os.path.exists(owners_file):
        return owners_file

    return find_owners_file(parent_dir)


commit_hashes = subprocess.call(GET_COMMITS_COMMAND).split('\n')

if not check_ownership(commit_hashes):
    print 'VREF/OWNERSHIP'  # I think this will trigger the rule to fail
