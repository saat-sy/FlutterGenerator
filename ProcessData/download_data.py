from github import Github
from datetime import datetime
import os
import shutil
from curtsies.fmtfuncs import red, bold, green, yellow, blue

begin_time = datetime.now()

def checkIfFlutter(url):
    list_of_required_dirs = [
        'lib',
        'android',
        'ios',
        'web',
        'pubspec.lock',
        'pubspec.yaml'
    ]

    urlIsFlutter = False

    for dir, sub_dirs, files in os.walk(url):
        if len(sub_dirs) >= 4 and len(files) >= 2:
            contents = sub_dirs + files
            
            flag = 0
            # CHECK IF ALL DIRS EXIST
            for f in contents:
                for l in list_of_required_dirs:
                    if l == f:
                        flag += 1

            if flag == 6:
                # CHECK IF MAIN.DART ALSO EXISTS (SAFETY)
                for d in os.listdir(os.path.join(dir, 'lib')):
                    if d == 'main.dart':
                        flag += 1

            if flag == 7:
                urlIsFlutter = True if dir == url else False
                if dir != url:
                    target_loc = url.split('/')[1] + ':' + dir.rsplit('/', 1)[1]
                    try:
                        shutil.move(dir, os.path.join('repos', target_loc))
                    except:
                        print(red('Already exists'))
                print(green(dir + " is a Flutter Folder"))

    if not urlIsFlutter:
        try:
            print(red(url + ' is not a flutter directory. Removed'))
        except:
            print('what!?')
        shutil.rmtree(url, ignore_errors=True)

total_count = len(os.listdir('repos/'))

status = open('status.txt', 'r').read()
start_time = int(status) - 86400
end_time = start_time - 86400

ACCESS_TOKEN = open('token.txt', "r").read()
g = Github(ACCESS_TOKEN)

for i in range(20):
    start_time_str = datetime.utcfromtimestamp(start_time).strftime('%Y-%m-%d')
    end_time_str = datetime.utcfromtimestamp(end_time).strftime('%Y-%m-%d')

    query = f'language:dart created:{end_time_str}..{start_time_str}'
    result = g.search_repositories(query=query)

    start_time -= 86400
    end_time -= 86400

    try:

        for repository in result:

            print(bold(blue('ITERATION ' + str(i))))
            print('\n')
            string = str(len(os.listdir('repos/')) - total_count) + ' REPOS DOWNLOADED'
            newstring = str(len(os.listdir('repos/'))) + ' ALREADY DOWNLOADED'
            print(bold(yellow(string)))
            print(bold(yellow(newstring)))
            print('\n')

            # COMPUTER: y the hell are you doing this to me!!????
            with open('status.txt', 'w') as status:
                status.write(str(start_time))
                status.close()

            if repository.clone_url.__contains__('github.com/flutter/'):
                continue

            os.system(
                f"git clone {repository.clone_url} repos/{repository.owner.login}:{repository.name}")

            checkIfFlutter(f"repos/{repository.owner.login}:{repository.name}")

            clear = lambda: os.system('clear')
            clear()

    except Exception as e:
        print(bold(red(str(e))))
        continue

print(bold(green(str(datetime.now() - begin_time))))