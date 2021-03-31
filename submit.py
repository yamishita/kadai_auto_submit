#####################################################################################
# This script is for submitting ad1 or ad2 report-data automatically.
# The structure of directy for running this script,
#  
# |-ex1(d)-----program(d)
# |          |
# |          |-etc(d)---------report-ex1.pdf
# |          |              |-report-ex1.tex
# |          |              |-result-ex1.txt
# |          |
# |          |-report-ex1.txt
# :
# |-submit.py
#
# The program directory will be arcived so its contents's structure is arbitrary.
# But, contents of etc directry must be this form, 'report-***.pdf report-***.tex...'
# and, the reportfile 'report-***.txt' must be this form, too.
#
# usage: like below (an example)
#   $python submit.py ex1
#
#####################################################################################
import os
import sys
import subprocess
import requests
import tarfile
import glob
from pprint import pprint

# command-line argument
# [script name] [report name(ex: ex6)]
if len(sys.argv) < 2:
    print('usage: python', sys.argv[0], '[report name(ex: ex6)]')
    sys.exit(0)

# needed parameter
# change these if you need
param = {
        'username': 'xxxxxxxx',
        'password': 'xxxxxxxx',
        'mode': 'make-report',
        'year': '2017',
        'class': 'X151',
        'report': sys.argv[1],
        }
# needed submit-data
# change these if you need
submit_data = {
        'report-txt': True,
        'program'   : True,
        'report-pdf': True,
        'report-tex': True,
        'result-txt': False,
        }

# find "report-.*\.txt" in currnet directry
rep_file = {}
# find "programs" directry and compress "tar.gz"
src_files = {}
# find "result-.*\.txt" in current directry
# and find "report-.*\.tex | report-.*\.pdf" in the "report" directry
etc_files = {}

def print_result(obj):
    print('===>',obj)
    #print('--- receiced data ---')
    #print(obj.text)
    #print('--- headers ---')
    #obj.headers

def fill_no_file():
    '''
    fill all form input of ???
    '''

def set_report_txt(challenge_name):
    print('\n--- set report-txt ---')
    print('report-txt:', str(submit_data['report-txt']))
    os.chdir(challenge_name)
    indir = os.listdir('.')
    reptxt = 'report-'+challenge_name+'.txt'
    if reptxt in indir:
        fileobj = open(reptxt, 'rt')
        rep_file['reportfile'] = (reptxt, fileobj, 'text/plain')
        print(reptxt)
    else:
        print('no report-txt!')
        return 1
    os.chdir('..')
    return 0

def set_program(challenge_name):
    '''
    compress the directory which has program files.
    if success to compress, set the data to the dict "src_files"
    '''
    print('\n--- set program-files ---')
    print('program:', str(submit_data['program']))
    os.chdir(challenge_name)
    indir = os.listdir('.')
    if submit_data['program']:
        if 'program' in indir:
            subprocess.call(['tar','-zcvf','program.tar.gz','program'])
            fileobj = tarfile.open('program.tar.gz','r:gz')
            src_files['source1'] = ('program.tar.gz', fileobj, 'application/gzip')
        else:
            print('no program directry!')
            return 1

    os.chdir('..')
    return 0 


def set_etc(challenge_name):
    '''
    set etc files
    param : kadai
    return: success- 0, otherwise- 1
    '''
    print('\n--- set etc-files ---')
    print('report-pdf:', str(submit_data['report-pdf']))
    print('report-tex:', str(submit_data['report-tex']))
    print('result-txt:', str(submit_data['result-txt']))
    os.chdir(challenge_name)
    indir = os.listdir('.')
    if 'etc' in indir:
        os.chdir('etc')
        indir = os.listdir('.') 
        # set pdf
        if submit_data['report-pdf']:
            pdf = 'report-'+challenge_name+'.pdf'
            if pdf in indir:
                fileobj = open(pdf, 'rb')
                etc_files['etc1'] = (pdf, fileobj, 'application/pdf')
                print('etc/'+pdf)
            else:
                print('no pdf!')
                return 1
        # set tex
        if submit_data['report-tex']:
             tex = 'report-'+challenge_name+'.tex'
             if tex in indir:
                 fileobj = open(tex, 'rt')
                 etc_files['etc2'] = (tex, fileobj, 'text/x-tex')
                 print('etc/'+tex)
             else:
                 print('no tex!')
                 return 1
        # set result-txt
        if submit_data['result-txt']:
            result = 'result-'+challenge_name+'.txt'
            if result in indir:
                fileobj = open(result, 'rt')
                etc_files['etc3'] = (result, fileobj, 'text/plain')
                print('etc/'+result)
            else:
                print('no result-txt!')
                return 1
        os.chdir('..')
    else:
        print('no etc directory!')
        return 1
    os.chdir('..')
    return 0 

# main script -----------------------------------------------------------------------

prefix_url = 'http://edu2.cs.inf.shizuoka.ac.jp'

#make a session
# this session means "http session", but "3-handshake-session"
# Without the system "http session", 
# it can't acsess same autherraized page at various tab in browser 
session = requests.Session()

#request the authentication
url = prefix_url+'/cgi-bin/auth.cgi'

print('HTTP POST',url[len(prefix_url):],'in session')
resp = session.post(url, data=param, allow_redirects=True)
print_result(resp) # -> logining...!

#request the submit-form
url =prefix_url+'/cgi-bin/make-report.cgi?'\
        'year='+param['year']+'&'\
        'amp;class='+param['class']+'&'\
        'amp;report='+param['report']

print('HTTP GET',url[len(prefix_url):],'in session')
resp = session.get(url)
print_result(resp)

#set files to submit-form
form_data = {
        'year': param['year'],
        'class': param['class'],
        'report': param['report'],
        }

# set submit-files
print('\n===>','make submit-data...')
r = set_report_txt(sys.argv[1])
if r != 0:
    print('Error: setting report-txt was failed!')
    sys.exit(0)
r = set_program(sys.argv[1])
if r != 0:
    print('Error: setting program was failed!')
    sys.exit(0)
r = set_etc(sys.argv[1])
if r != 0:
    print('Error: setting etc was failed!')
    sys.exit(0)
# make form_data
form_data.update(rep_file)
form_data.update(src_files)
form_data.update(etc_files)
# verify cleated form-data
print('\n===>','verify form-data...')
pprint(form_data)

#submit
url = prefix_url+'/cgi-bin/submit-report.cgi'
print('HTTP POST',url[len(prefix_url):],'in session')
resp = session.post(url, files=form_data) 
print_result(resp)

