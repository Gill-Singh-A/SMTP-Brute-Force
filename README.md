# SMTP Brute Force
A Python Program that uses **smtplib** module to brute force SMTP (Simple Mail Transver Protocol) Server
## Requirements
Language Used = Python3<br />
Modules/Packages used:
* smtplib
* datetime
* optparse
* colorama
* multiprocessing
* time
<!-- -->
Install the dependencies:
```bash
pip install -r requirements.txt
```
## Arguments
* '-s', "--server" : Target SMTP Server
* '-p', "--port" : Port of Target SMTP Server (Default=25)
* '-u', "--users" : Target Users (seperated by ',') or File containing List of Users
* '-P', "--password" : Passwords (seperated by ',') or File containing List of Passwords
* '-c', "--credentials" : Name of File containing Credentials in format ({user}:{password})
* '-w', "--write" : CSV File to Dump Successful Logins (default=current data and time)