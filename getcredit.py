#!/usr/bin/env python3
import argparse
import fnmatch
import glob
import gzip
import os
import re
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
                        if words[4] != '12' and words[6] == 'c':
                            credit.append(words)
    return credit


def write_file(fileout, credit):
    header = 'switch port pid wwn credit fsz class service alias'.split()

    with open(fileout, 'w') as ftext:
        print('{:12s} {:8s} {:8s} {:26s} {:8s} {:8s} {:8s} {:14s} {}'.format(*header), file=ftext)

        for item in credit:
            print('{:12s} {:8s} {:8s} {:26s} {:8s} {:8s} {:8s} {:14s} {}'.format(*item), file=ftext)


def main():
    outlist = []
#    dinput = '/tmp/ss'
    output = '/tmp/out'

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-i', '--dinput', help='Directory with supportsave files', required=True)
    args = parser.parse_args()

    dinput = args.dinput

    try:
        if os.path.isdir(dinput) and fnmatch.filter(os.listdir(dinput), '*.zip'):

            with tempfile.TemporaryDirectory() as tempdir:
                print('The created temp directory is %s.' % tempdir)

            if not os.path.exists(output):
                try:
                    os.mkdir(output)
                except Exception as e:
                    print('Unable to create directory %s.' % output)

            for files in os.listdir(dinput):
                if fnmatch.fnmatch(files, '*.zip'):
                    zip = zipfile.ZipFile(os.path.join(dinput, files))
                    f = zipfile.ZipFile.namelist(zip)
                    switch = re.findall(r'(?<=\_)\w*(?=\_)', files)
                    datass = re.findall(r'(?<=\_)\d+', files)
                    fileout = os.path.join(output, ''.join(datass)) + '.out'
                    print('Wait processed {} supportsave.'.format(*switch))
                    for item in f:
                        if re.findall(r'SSHOW_SYS.txt', item):
                            alias = get_alias(zip, item, tempdir)

                        if re.findall(r'SSHOW_PORT.txt', item):
                            credit = get_credit(zip, switch, alias, item, tempdir)

                outlist += credit

            outlist.sort(key=lambda x: (x[4], x[8]), reverse=False)
            write_file(fileout, outlist)
            print('See file collection: %s' % fileout)

            try:
                shutil.rmtree(tempdir)
                print("Temp directory '%s' has been removed successfully." % tempdir)
            except OSError as e:
                print('Delete of the directory %s failed.' % tempdir, e)
        else:
            print('Directory %s is empty or does not exist.' % dinput)
            print('Specify a different directory of the file format: supportsave_switchname_YYYYMMDDHHMM.zip')
            exit(1)

    except FileNotFoundError as e:
        print(e)
        exit(1)



if __name__ == '__main__':
    main()
