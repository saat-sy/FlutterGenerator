FILE = 'rendered_filenames.txt'

for file in open(FILE, 'r').readlines():
    file = file.replace('\n', '')
    f = open(file, 'r').read()
    # if f.startswith('b\''):
        # f = f[2:-1]
    f = f.replace('\\', '')
    with open(file, 'w') as w:
        w.write(f)  