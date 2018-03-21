#!/usr/bin/python
# Description: simple nagios plugin to check WAN download/upload speed
#              via FTP.
# Author: Florian Paul Hoberg <florian [at] hoberg.ch>

import ftplib
import timeit
import time
import os
import sys
import argparse

def download(ftpsession, remote_filename, local_filename, remote_directory_download):
    """ download remote speedtest file """
    start = timeit.default_timer()
    ftpsession.cwd(remote_directory_download)
    ftpsession.retrbinary('RETR ' + remote_filename, local_filename.write, 1024)
    stop = timeit.default_timer()
    dl_time = stop - start
    return dl_time

def upload(ftpsession, remote_filename, local_filename_read, remote_directory_upload, timestamp):
    """ upload local speedtest file """
    start = timeit.default_timer()
    ftpsession.cwd(remote_directory_upload)
    ftpsession.storbinary('STOR ' + remote_filename + str(timestamp), local_filename_read)
    ftpsession.quit()
    stop = timeit.default_timer()
    ul_time = stop - start
    return ul_time

def get_filesize(local_filename):
    """ calculate filesize """
    file_size = os.path.getsize( local_filename )
    return file_size

def get_mbit(file_size, time):
    """ convert MB to Mbit """
    mbit = float(file_size) / 1024 / 1024 / float(time) / float ("0.125")
    return mbit

def compare_values(real_mbit, warn_mbit, crit_mbit):
    """ compare values and generate exitcode """
    if real_mbit < warn_mbit:
        if real_mbit > crit_mbit:
            exit_code = 1 
            return exit_code
        else:
            exit_code = 2
            return exit_code
    else:
        exit_code = 0
        return exit_code 

def main():
    """ """
    argparser = argparse.ArgumentParser(description='Following options are possible:')
    argparser.add_argument('-H', '--host', type=str, help='remote FTP host')
    argparser.add_argument('-P', '--port', type=int, help='remote FTP port')
    argparser.add_argument('-U', '--user', type=str, help='remote FTP user')
    argparser.add_argument('-p', '--password', type=str, help='remote FTP password')
    argparser.add_argument('-f', '--remote-file-name', type=str, help='remote FTP file')
    argparser.add_argument('-Dl', '--remote-download-dir', type=str, help='remote FTP directory for download')
    argparser.add_argument('-Du', '--remote-upload-dir', type=str, help='remote FTP directory for upload')
    argparser.add_argument('-wd', '--warn-download', type=int, help='warn for download (Mbit)')
    argparser.add_argument('-wu', '--warn-upload', type=int, help='warn for upload (Mbit)')
    argparser.add_argument('-cd', '--crit-download', type=int, help='critical for download (Mbit)')
    argparser.add_argument('-cu', '--crit-upload', type=int, help='critical for upload (Mbit)')
    cliargs = argparser.parse_args()

    if  cliargs.host is None:
        cliargs.host = 'ftp.hoberg.ch' 
    ftp_server_address = cliargs.host

    if  cliargs.port is None:
        cliargs.port = 21
    ftp_server_port = cliargs.port

    if  cliargs.user is None:
        cliargs.user = 'anonymous'
    ftp_server_user = cliargs.user

    if  cliargs.password is None:
        cliargs.password = 'no-pass'
    ftp_server_pass = cliargs.password

    if  cliargs.remote_file_name is None:
        cliargs.remote_file_name = '100MB.zip'
    remote_filename = cliargs.remote_file_name

    if  cliargs.remote_download_dir is None:
        cliargs.remote_download_dir = '/'
    remote_directory_download = cliargs.remote_download_dir

    if  cliargs.remote_upload_dir is None:
        cliargs.remote_upload_dir = '/upload'
    remote_directory_upload = cliargs.remote_upload_dir

    speedchecks = [cliargs.warn_download, cliargs.crit_download, cliargs.warn_upload, cliargs.crit_upload]
    timestamp = time.time()
    ftpsession = ftplib.FTP(ftp_server_address, ftp_server_user, ftp_server_pass)
    local_filename = open(remote_filename, 'wb')
    local_filename_read = open(remote_filename, 'rb')
    dl_time = download(ftpsession, remote_filename, local_filename, remote_directory_download)
    ul_time = upload(ftpsession, remote_filename, local_filename_read, remote_directory_upload, timestamp)
    file_size = get_filesize(remote_filename)
    dl_mbit = get_mbit(file_size, dl_time)
    ul_mbit = get_mbit(file_size, ul_time)

    for single_check in speedchecks:
        if single_check is not None:
            exit_code = compare_values(dl_mbit, cliargs.warn_download, cliargs.crit_download) 
            print "Filesize: " + str(file_size / 1024 / 1024) + " MB | Download Speed: " + str(round(dl_mbit,2)) + " Mbit | Upload Speed: " + str(round(ul_mbit,2)) + " Mbit | Exitcode: " + str(exit_code)
            sys.exit(exit_code)
        else:
            print "Filesize: " + str(file_size / 1024 / 1024) + " MB | Download Speed: " + str(round(dl_mbit,2)) + " Mbit | Upload Speed: " + str(round(ul_mbit,2)) + " Mbit"
            exit_code = 0
            sys.exit(exit_code)

main()
