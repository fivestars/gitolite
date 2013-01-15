import os
import subprocess
import sys

from ownership_utils import build_commit_to_acceptors_dict, get_files, p,\
                            splitpath, find_git_hash


username_to_phid = dict((user['userName'], user['phid']) for user in p.user.query())

oldsha, newsha = sys.argv[1:3]  # oldsha and newsha are passed in as first and second arguments

gl_user = os.environ['GL_USER']
user_phid = (phid for username, phid in username_to_phid.items() if username == gl_user).next()

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
        accepted_by = commit_to_acceptors[commit_hash] | set([user_phid])

        for f in files_in_commit:
            code_owners = [username_to_phid[user] for user in get_owners(oldsha, f)]
            if not (set(accepted_by) & set(code_owners)):
                print CHECK_FAIL_MESSAGE.format(filename=f, commit_hash=commit_hash)
                return False

    return True


def get_owners(oldsha, path):
    """Crawls up directory tree to until it finds a .owners file

    path is relative to top project dir"""
    owners_hash = ''
    next_dir = ''
    path_parts = splitpath(path)

    for i in range(len(path_parts)):
        ls_tree = subprocess.Popen('git ls-tree {git_hash}'.format(git_hash=(next_dir or oldsha)),
                shell=True, stdout=subprocess.PIPE).stdout.read().split('\n')
        owners_hash = find_git_hash(ls_tree, '.owners') or owners_hash
        next_dir = find_git_hash(ls_tree, path_parts[i])

    owners_file_contents = subprocess.Popen('git cat-file -p {git_hash}'.format(git_hash=owners_hash),
            shell=True, stdout=subprocess.PIPE).stdout.read()

    owners = [line.strip() for line in owners_file_contents.split() if not line.startswith('#')]

    return owners


commit_hashes = subprocess.Popen(GET_COMMITS_COMMAND,
    shell=True, stdout=subprocess.PIPE).stdout.read().split()

if not check_ownership(commit_hashes):
    print 'VREF/OWNERSHIP'
