#!/usr/bin/env python3
import fnmatch
import gzip
import re, os
import shutil
import tempfile
import zipfile


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


def get_credit(switch, item, tempdir):
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
                words = switch + pndx + match.group().replace(' ', ' ').split()
                del words[2]
                credit.append(words)

    return credit


def write_file(fileout, alias, credit):
    with open(fileout, 'a') as ftext:
        header = 'switch port pid wwn credit fsz class service alias'.split()
        #    print('{:12s} {:8s} {:8s} {:26s} {:8s} {:8s} {:8s} {:14s} {}'.format(*header))
        print('{:12s} {:8s} {:8s} {:26s} {:8s} {:8s} {:8s} {:14s} {}'.format(*header), file=ftext)

        for item in credit:
            wwn = item[3]
            for row in alias:
                if row[1] == wwn:
                    credit = item + row[0].split()
                    #                print('{:12s} {:8s} {:8s} {:26s} {:8s} {:8s} {:8s} {:14s} {}'.format(*credit))
                    print('{:12s} {:8s} {:8s} {:26s} {:8s} {:8s} {:8s} {:14s} {}'.format(*credit), file=ftext)


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
            datass = re.findall(r'(?<=\_)\d+', files)
            fileout = os.path.join(''.join(datass)) + '.out'
            for item in f:
                if re.findall(r'SSHOW_SYS.txt', item):
                    alias = get_alias(item, tempdir)

                if re.findall(r'SSHOW_PORT.txt', item):
                    credit = get_credit(switch, item, tempdir)

            credit.sort(key=lambda x: x[4], reverse=False)

            write_file(fileout, alias, credit)

    try:
        shutil.rmtree(tempdir)
        print("Directory '%s' has been removed successfully" % tempdir)
    except OSError as e:
        print('Delete of the directory %s failed' % tempdir, e)

    print('See file collection: %s' % fileout)


if __name__ == '__main__':
    main()
