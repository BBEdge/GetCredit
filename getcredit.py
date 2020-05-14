#!/usr/bin/env python3


import fnmatch
import gzip
import re, os
import shutil
import tempfile
import zipfile

'''   
    DATA SS REGEX: (?<=\_)\d+
    ALIAS REGEX: alias.(\w*):(\S*)
    OUTPUT FORMAT: switch, pid, wwn, credit, fsz, class, sname, alias
    ^portloginshow\s(\d+)
'''


def get_alias(item, tempdir):
    alias = []

    zip.extract(item, tempdir)
    gz = os.path.join(tempdir, item)

    with gzip.open(gz, 'rt', encoding='utf8', errors='ignore') as f:
        for line in f:
            match = re.search(r'alias.(\w*):(\S*)', line)
            if match:
                words = (match.group(1) + ' ' + match.group(2).replace(';', ' ')).split()
                alias.append(words)

    return alias


def get_credit(switch, alias, item, tempdir):
    credit = []
    skip = True

    zip.extract(item, tempdir)
    gz = os.path.join(tempdir, item)

    with gzip.open(gz, 'rt', encoding='utf8', errors='ignore') as f:
        for line in f:
            match = re.search(r'^portloginshow\s(\d+)', line)
            if match:
                pid = match.group(1).split()
                words = switch + pid
#                print(words)
#                words = (switch + credit)

#    print(words)
    return credit


def main():
    global zip
    dinput = '/tmp/ss'
    output = '/tmp/out'

    with tempfile.TemporaryDirectory() as tempdir:
        print('The created temporary directory is %s' % tempdir)

    for files in os.listdir(dinput):
        if fnmatch.fnmatch(files, '*.zip'):
            zip = zipfile.ZipFile(os.path.join(dinput, files))
            f = zipfile.ZipFile.namelist(zip)
            switch = re.findall(r'(?<=\_)\w*(?=\_)', files)
            for item in f:
                if re.findall(r'SSHOW_SYS.txt', item):
                    alias = get_alias(item, tempdir)

                if re.findall(r'SSHOW_PORT.txt', item):
                    credit = get_credit(switch, alias, item, tempdir)

#    for item in alias:
#        print(item)

    try:
        shutil.rmtree(tempdir)
        print("Directory '%s' has been removed successfully" % tempdir)
    except OSError as e:
        print('Delete of the directory %s failed' % tempdir, e)


if __name__ == '__main__':
    main()
