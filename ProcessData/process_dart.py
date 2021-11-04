import os
import shutil
from curtsies.fmtfuncs import red, green, yellow
import fileinput
from tqdm import tqdm

FOLDER = 'repos'

def checkForImports(file):
    # RETURNS TRUE IF IT IS A VALID FILE WITH NO USELESS PACKAGES

    try:

        for line in file.splitlines():
            if line.startswith('import'):
                try:
                    package = line[(line.find(':')+1):line.find('/')]
                except:
                    continue
                
                with open('useless_packages.txt') as useless:
                    for useless_line in useless.read().splitlines():
                        useless_package = useless_line[:useless_line.find(':')]
                        if useless_package == package:
                            return False
                    useless.close()

    except:
        return False

    return True

def checkForWidget(listOfFiles):

    # CHECK FOR WIDGETS IN USEFUL_FILES
    # AND RETURN LIST OF FILES THAT ARE ALL WIDGETS

    new_list = []
    

    for file in listOfFiles:

        try:

            # OPEN DART FILES
            with open(file, 'r') as dartFile:
                for line in dartFile.read().splitlines():
                    if line.startswith('class'):
                        if line.__contains__('StatelessWidget') or line.__contains__('StatefulWidget'):
                            new_list.append(file)
                            break
                dartFile.close()
        
        except:

            continue

    return new_list

def createFileClassDict(listOfFiles):

    new_dict = {}

    for file in listOfFiles:
        # OPEN DART FILES

        try:

            with open(file, 'r') as dartFile:
                for line in dartFile.read().splitlines():
                    if line.startswith('class'):
                        
                        if line.__contains__('StatelessWidget') or line.__contains__('StatefulWidget'):
                            classname = line[6:(line.find('extends') - 1)]
                            new_dict[file] = classname

                        else:
                            continue
                        
                dartFile.close()

        except:
            continue
        
    return new_dict
                    
def copyPasteClasses(listOfFiles, dict, original_files):

    def copyandpaste(fromFileLoc, toFileLoc):

        fromImports = []
        toImports = []
        extra_imports = []

        lines_to_copy = []

        # EXTRA IMPORTS
        with open(fromFileLoc, 'r+') as fromFile, open(toFileLoc, 'r+') as toFile:

            for l_from in fromFile.readlines():
                if l_from.rstrip().startswith('import'):
                    fromImports.append(l_from)

            for l_to in toFile.readlines():
                if l_to.rstrip().startswith('import'):
                    toImports.append(l_to)

            for frm in fromImports:
                if frm in toImports:
                    fromImports.remove(frm)

            extra_imports = fromImports

            fromFile.close()
            toFile.close()

        # WRITING IMPORTS
        if len(extra_imports) != 0:
            added = False
            for line in fileinput.FileInput(toFileLoc, inplace=True):
                if 'import' in line and not added:
                    line = line.rstrip()
                    text_to_replace = line + '\n'
                    for e in extra_imports:
                        text_to_replace += e + '\n'
                    line = line.replace(line, text_to_replace)
                    added = True
                # THIS PRINT IS FOR FILEINPUT, DONOT REMOVE 
                print(line, end="")

        # WRITING THE REST OF THE FILE
        with open(fromFileLoc, 'r+') as fromFile, open(toFileLoc, 'a+') as toFile:
            opening_count = 0
            class_found = False
            found_parenthesis = False
            for line in fromFile.readlines():
                try:
                    if line.rstrip().startswith('class'):
                        class_found = True
                    if class_found:
                        if '{' in line:
                            opening_count += 1
                        if '}' in line:
                            opening_count -= 1

                        if opening_count > 0 or opening_count < 0:
                            found_parenthesis = True
                            
                        lines_to_copy.append(line)

                    if found_parenthesis:    
                        if opening_count == 0:
                            class_found = found_parenthesis = False
                except:
                    continue
            
            toFile.write('\n')
            for l in lines_to_copy:
                toFile.write(l)

            fromFile.close()
            toFile.close()
    
    def delete(file, keyword):
        opened = False
        found_para = False # WILL BE TRUE ONLY WHEN IT FINDS opened_index >or< 0
        opened_index = 0
        for line in fileinput.FileInput(file, inplace=True):
            try:
                if keyword in line:
                    opened = True
                if opened:
                    if '(' in line:
                        opened_index += 1
                    if ')' in line:
                        opened_index -= 1
                    # IF THE FIRST LINE ONLY DOESN'T HAVE (
                    if opened_index > 0 or opened_index < 0:
                        found_para = True
                if not opened:
                    print(line, end="")
                if found_para:
                    if opened_index == 0:
                        opened = False
                        found_para = False
            except:
                continue
    
    for file in listOfFiles:
        try:
            nothing_to_paste = False
            already_pasted = []
            while True:
                with open(file, 'r') as dartFile:
                    paste = False
                    for line in dartFile.readlines():
                        importname = ''
                        if line.startswith('import'):
                            importname = line[line.rfind('/')+1 : -3]
                        
                            # CHECK IF THIS IMPORT NAME IS PRESENT IN THE ORFILES
                            if importname == 'material.dart':
                                continue
                            for orFile in original_files:
                                orImport = orFile[orFile.rfind('/')+1 : ]
                                if importname == orImport and importname not in already_pasted:
                                    if orFile in listOfFiles:
                                        paste = True
                                        copyandpaste(orFile, file)
                                        already_pasted.append(importname)
                                        break
                                    else:
                                        keyword = dict[orFile]
                                        delete(file, keyword)

                        # TO BREAK FROM THE FOR LOOP
                        # ALSO CHECK IF ANY EXTRA_IMPORTS ARE PENDING
                        if paste:
                            break
                        else:
                            nothing_to_paste = True

                        dartFile.close()

                # TO BREAK FROM THE WHILE LOOP
                if nothing_to_paste:
                    break
        
        except:
            continue
                
def replaceImage(useful_files):

    for file in useful_files:
        try:
            next_line = False

            for line in fileinput.FileInput(file, inplace=True):

                if next_line:
                    if ',' in line:
                        line = '\'url\',\n'
                    else:
                        line = '\'url\'\n'
                    next_line = False

                if 'AssetImage' in line \
                    or 'NetworkImage' in line \
                        or 'MemoryImage' in line \
                            or 'FileImage' in line:
                    
                    tabs = line[:line.find('image')]
                    line = tabs + f'image: NetworkImage(\'url\'),' + line[line.find(',')+1:] 

                if 'Image.network' in line \
                    or 'Image.asset' in line \
                        or 'Image.memory' in line \
                            or 'Image.file' in line:

                    if '.asset' in line:
                        line = line.replace('asset', 'network')

                    if '.memory' in line:
                        line = line.replace('memory', 'network')

                    if '.file' in line:
                        line = line.replace('file', 'network')
                    
                    if '(' in line and ')' in line:
                        if ',' in line:
                            if line.find(',') < line.find(')'):
                                line = line[:line.find('(') + 1] + '\'url\'' + line[line.find(','):]
                            else:
                                line = line[:line.find('(') + 1] + '\'url\'),'
                        else:
                            line = line[:line.find('(') + 1] + '\'url\'),'

                    elif '(' in line:
                        next_line = True

                print(line, end="")

        except:
            continue

def replaceText(useful_files):

    for file in useful_files:
        try:
            next_line = False

            for line in fileinput.FileInput(file, inplace=True):

                if next_line:
                    if line.count('\'') >= 2 or line.count('\"') >= 2:
                        pass
                    else:
                        if ',' in line:
                            for char in line:
                                if char.isspace():
                                    continue
                                else:
                                    line = line[:line.find(char)-1] + '\'' + line[line.find(char):]
                                    break
                            line = line[:line.find(',')] + '\'' + line[line.index(','):]
                        else:
                            for char in line:
                                if char.isspace():
                                    continue
                                else:
                                    line = line[:line.find(char)-1] + '\'' + line[line.find(char):]
                                    break
                            line = line[:line.find('\n')] + '\'' + line[line.index('\n'):]
                    next_line = False

                if 'Text' in line:

                    if '(' in line and ')' in line:
                        if line.count('\'') >= 2 or line.count('\"') >= 2:
                            pass
                        
                        else: 
                            if ',' in line:
                                if line.find(',') < line.find(')'):
                                    line = line[:line.find('(')+1] + '\'' + \
                                        line[line.find('(')+1:line.find(',')] + '\'' + \
                                            line[line.find(','):]
                                else:
                                    line = line[:line.find('(')+1] + '\'' + \
                                        line[line.find('(')+1:line.find(')')] + '\'' + \
                                            line[line.find(')'):]

                    elif '(' in line:
                        next_line = True

                line = line.replace('$', '')
                print(line, end="")
        
        except:
            continue

def addRunApp(useful_files, dict):

    for file in useful_files:
        try:
            if 'main.dart' in file:
                import_added = False
                for line in fileinput.FileInput(file, inplace=True):
                    if 'import' in line:
                        if not import_added:
                            print('import \'package:flutter/material.dart\';')
                            import_added = True
                            continue
                    elif 'MaterialApp(' in line:
                        line = line + 'debugShowCheckedModeBanner: false,'
                        print(line)
                    else:
                        print(line, end="")
                continue

            classname = dict[file]
            
            lines_to_add = [
                'import \'package:flutter/material.dart\';',
                'void main() {',
                '    runApp(MyApp());',
                '}',
                'class MyApp extends StatelessWidget {',
                '// This widget is the root of your application.',
                '@override',
                'Widget build(BuildContext context) {',
                '    return MaterialApp(',
                '        debugShowCheckedModeBanner: false,',
                '        title: \'Title\',',
                '        theme: ThemeData(',
                '            primarySwatch: Colors.blue,',
                '        ),',
                f'        home: {classname}(),',
                '        );',
                '    }',
                '}'
            ]

            l_added = False
            for line in fileinput.FileInput(file, inplace=True):
                if not l_added:
                    for l_to_add in lines_to_add:
                        print(l_to_add)
                    l_added = True

                if not 'import' in line:
                    print(line, end="")

        except:
            continue

def rmClassOverride(useful_files):
    for file in useful_files:
        try:
            stop = False
            stateful = False 

            for line in fileinput.FileInput(file, inplace=True):

                if 'class' in line and 'MyApp' not in line:

                    if 'StatefulWidget' in line:
                        stateful = True

                    if not '{' in line:
                        line = line + '{'

                    print(line, end="")
                    stop = True

                if stateful and 'createState()' in line:
                    print('@override')
                    stop = False
                
                if 'Widget build(BuildContext context)' in line:
                    print('@override')
                    stop = False

                if not stop:
                    print(line, end="")

        except:
            continue

def removeFunctions(useful_files):
    for file in useful_files:
        try: 
            wait = False
            for line in fileinput.FileInput(file, inplace=True):
                if line.strip().startswith('on'):
                    print(line[:line.find(':')] + ' : () {},')
                    if '}' not in line and '{' in line:
                        wait = True
                    continue

                if wait and '}' in line:
                    wait = False

                if not wait:
                    print(line, end="")
        except:
            continue

for repo in tqdm(os.listdir(FOLDER)):

    files = []
    useful_files = []
    file_class_dict = {}

    # COLLECTING ALL FILE PATHS
    for dirPath, subdir, file in os.walk(os.path.join(FOLDER, repo, 'lib')):
        for fs in file:
            files.append(os.path.join(dirPath, fs))

    try:
        file_class_dict = createFileClassDict(files)
    except:
        print(red('error occured in file_class_dict'))
        with open('process_error_log.txt', 'a') as errors:
            errors.write(repo + ' error occured in file_class_dict\n')
            errors.close()
        continue

    # OPENING ALL FILE PATHS
    for f in files:
        with open(f, 'r') as file:
            try:
                imports = checkForImports(file.read())
            except:
                continue
        if imports:
            useful_files.append(f)
    
    if len(useful_files) == 0:
        # REMOVE USELESS REPO
        try:
            shutil.rmtree(os.path.join(FOLDER, repo), ignore_errors=True)
        except:
            pass
        continue

    try:
        new_list = checkForWidget(useful_files)
    except:
        print(red('error occured in checkForWidget'))
        with open('process_error_log.txt', 'a') as errors:
            errors.write(repo + ' error occured in checkForWidget\n')
            errors.close()
        continue
    useful_files = new_list

    for file in files:
        if not file in useful_files:
            try:
                os.remove(file)
            except:
                pass


    # RUNNING ALL THE FUNCTIONS
    
    try:
        copyPasteClasses(useful_files, file_class_dict, files)
    except:
        print(red('error occured in copyPasteClasses'))
        with open('process_error_log.txt', 'a') as errors:
            errors.write(repo + ' error occured in copyPasteClasses\n')
            errors.close()
        continue

    try:
        addRunApp(useful_files, file_class_dict)
    except:
        print(red('error occured in addRunApp'))
        with open('process_error_log.txt', 'a') as errors:
            errors.write(repo + ' error occured in addRunApp\n')
            errors.close()
        continue

    try:
        replaceImage(useful_files)
    except:
        print(red('error occured in replaceImage'))
        with open('process_error_log.txt', 'a') as errors:
            errors.write(repo + ' error occured in replaceImage\n')
            errors.close()
        continue

    try:
        replaceText(useful_files)
    except:
        print(red('error occured in replaceText'))
        with open('process_error_log.txt', 'a') as errors:
            errors.write(repo + ' error occured in replaceText\n')
            errors.close()
        continue

    try:
        rmClassOverride(useful_files)
    except:
        print(red('error occured in rmOverride'))
        with open('process_error_log.txt', 'a') as errors:
            errors.write(repo + ' error occured in rmOverride\n')
            errors.close()
        continue

    try:
        removeFunctions(useful_files)
    except Exception as e:
        print(red('error occured in removeFunctions'))
        with open('process_error_log.txt', 'a') as errors:
            errors.write(repo + ' error occured in removeFunctions\n')
            errors.close()
        continue