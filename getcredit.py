#!/usr/bin/env python3
import fnmatch
import gzip
import re, os
import shutil
import tempfile
import zipfile


def get_alias(zip, item, tempdir):
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


def get_credit(zip, switch, alias, item, tempdir):
    credit = []

    zip.extract(item, tempdir)
    gz = os.path.join(tempdir, item)

    with gzip.open(gz, 'rt', encoding='utf8', errors='ignore') as f:
        for line in f:
            match = re.search(r'^portloginshow\s(\d+)', line)
            if match:
                pndx = match.group(1).split()

            match = re.search(r'ff\s+\w+\s+((?:[0-9a-fA-F]:?){16})\s+\d+\s+\d+\s+\w+\s+\w+=\w+', line)
            if match:
                for item in alias:
                    if match.group(1) == item[1]:
                        words = switch + pndx + match.group().replace(' ', ' ').split() + item[0].split()
                        del words[2]
                        if words[6] == 'c':
                            credit.append(words)
#                            print(words)
    return credit


def write_file(fileout, credit):
    with open(fileout, 'a') as ftext:
        header = 'switch port pid wwn credit fsz class service alias'.split()
        print('{:12s} {:8s} {:8s} {:26s} {:8s} {:8s} {:8s} {:14s} {}'.format(*header), file=ftext)

        for item in credit:
            print('{:12s} {:8s} {:8s} {:26s} {:8s} {:8s} {:8s} {:14s} {}'.format(*item), file=ftext)


def main():
    dinput = '/tmp/ss'
    output = '/tmp/out'

    with tempfile.TemporaryDirectory() as tempdir:
        print('The created temporary directory is %s' % tempdir)

    for files in os.listdir(dinput):
        if fnmatch.fnmatch(files, '*.zip'):
            zip = zipfile.ZipFile(os.path.join(dinput, files))
            f = zipfile.ZipFile.namelist(zip)
            switch = re.findall(r'(?<=\_)\w*(?=\_)', files)
            datass = re.findall(r'(?<=\_)\d+', files)
            fileout = os.path.join(''.join(datass)) + '.out'
            for item in f:
                if re.findall(r'SSHOW_SYS.txt', item):
                    alias = get_alias(zip, item, tempdir)

                if re.findall(r'SSHOW_PORT.txt', item):
                    credit = get_credit(zip, switch, alias, item, tempdir)

            credit.sort(key=lambda x: (x[4], x[8]), reverse=False)
            write_file(fileout, credit)

    try:
        shutil.rmtree(tempdir)
        print("Directory '%s' has been removed successfully" % tempdir)
    except OSError as e:
        print('Delete of the directory %s failed' % tempdir, e)

    print('See file collection: %s' % fileout)


if __name__ == '__main__':
    main()
