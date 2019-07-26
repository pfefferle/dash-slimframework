from bs4 import BeautifulSoup
import requests

import subprocess
import time
import sys
import os

PACKAGE = 'slim/slim'
DOCSET = 'Slim_Framework.docset'
PACKED = 'Slim_Framework.tgz'
ENTRIES = ['Slim_Framework.xml', 'SlimFramework.xml']

try:
    GH_TOKEN = os.environ['GH_TOKEN']
except:
    print('Please set `GH_TOKEN` environment variable', file=sys.stderr)
    sys.exit(1)

try:
    GH_REPO = os.environ['TRAVIS_REPO_SLUG']
except:
    print('Make sure that this script is called from Travis CI', file=sys.stderr)
    sys.exit(1)

def execute(*command, stdout=False, stderr=True):
    FNULL = open(os.devnull, 'w')

    if stdout: stdout = sys.stdout
    else: stdout = FNULL

    if stderr: stderr = sys.stderr
    else: stderr = FNULL

    return subprocess.call(command, stdout=stdout, stderr=stderr)

def get_all_versions(package):
    url = 'https://packagist.org/packages/' + package + '.json'

    response = requests.get(url=url)
    data = response.json()

    return data['package']['versions']

def get_latest_version(versions):
    for version in versions:
        if not any(x in version.lower() for x in ['dev', 'alpha', 'beta', 'rc']):
            return version

def get_current_version(filename):
    soup = BeautifulSoup(open(filename), 'html.parser')
    return soup.find('version').string

def update_entry_file(filename, old, new):
    content = open(filename).read()

    url1 = 'https://github.com/' + GH_REPO + '/releases/download/v'
    url2 = '/Slim_Framework.tgz'

    content = content.replace('<version>' + old + '</version>', '<version>' + new + '</version>')
    content = content.replace('<url>' + url1 + old + url2 + '</url>', '<url>' + url1 + new + url2 + '</url>')

    open(filename, 'w').write(content)

def main(package, docset, packed, entries):
    versions = get_all_versions(package)
    latest = get_latest_version(versions)

    current = get_current_version(entries[0])

    print('Latest version:', latest)
    print('Current version:', current)
    print()

    if latest == current:
        print('Already latest version')
        print('Canceling')
        sys.exit(0)

    print('Setting up Git')
    execute('git', 'config', 'user.name', 'Deployment Bot (from Travis CI)')
    execute('git', 'config', 'user.email', 'deploy@travis-ci.org')
    execute('git', 'config', 'push.followTags', 'true')
    execute('git', 'checkout', '-qf', 'master')


    print('Syncing documentation')
    st1 = execute('sh', 'sync.sh')

    print('Rebuilding documentation')
    st2 = execute(sys.executable, 'rebuild.py')

    print('Packing documentation')
    st3 = execute('sh', 'pack.sh', stderr=False)

    if st1 or st2 or st3:
        print('Error while generating documentation', file=sys.stderr)
        sys.exit(1)

    print('Updating entry files')
    for filename in entries:
        update_entry_file(filename, current, latest)

    print('Adding to stage')
    for filename in [docset, packed] + entries:
        execute('git', 'add', filename)

    print('Commiting changes')
    execute('git', 'commit', '-m', '[ci skip] Update docset to Slim ' + latest)

    print('Tagging changes')
    execute('git', 'tag', '-a', 'v' + latest, '-m', 'Docset for Slim ' + latest)

    print('Pushing changes')
    st = execute('git', 'push', '--set-upstream', 'https://' + GH_TOKEN + '@github.com/' + GH_REPO + '.git', 'master', stderr=False)

    if st:
        print('Something went wrong while publishing', file=sys.stderr)
        print('Make sure that `GH_TOKEN` contains correct token', file=sys.stderr)
        sys.exit(1)

    print('Sleeping before releasing')
    time.sleep(10)

    print('Releasing from Travis CI')
    sys.exit(0)

main(PACKAGE, DOCSET, PACKED, ENTRIES)
