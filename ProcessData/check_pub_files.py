import os
from tqdm import tqdm

PATH = 'repos/'

for folder in tqdm(os.listdir(PATH)):
    folder_path = os.path.join(PATH, folder)

    for file in os.listdir(folder_path):

        if file == 'pubspec.yaml':
            pub = open(os.path.join(folder_path, file), 'r').read()

            found_d = False            
            for line in pub.splitlines():

                if line.startswith('#'):
                    continue

                if line == 'dependencies:':
                    found_d = True
                    continue

                if line == 'dev_dependencies:':
                    found_d = False
                    break
                
                present = False
                if found_d:
                    l = line.strip()
                    for p in open('pub_packages.txt', 'r').read().splitlines():
                        if p[:p.find(':')] == l[:l.find(':')]:
                            present = True

                    if not present:
                        with open('pub_packages.txt', 'a') as packages:
                            if not l.startswith('#'):    
                                packages.write(l + '\n')