"""
GuardMail by Andrei

GuardMail is a simple python task that constantly polls an email address for new
steam-guard-codes and inserts them into a postgres database.
"""

import sys, getpass, time, re, psycopg2
from gmail import Gmail

def open_database_connection(pw):
    return psycopg2.connect("host=104.171.118.100 port=50432 dbname=emporium user=emporium password=%s" % pw)

if len(sys.argv) <= 1:
    print "Usage: ./guardmail.py <email>"
    sys.exit(1)

db_password = getpass.getpass("DB Password > ")
email_password = getpass.getpass("Email Password > ")

db = open_database_connection(db_password)

def store_code(email, username, code):
    global db

    while db.closed:
        print "DB Connection is closed, attempting to reopen"
        db = open_database_connection(db_password)
        time.sleep(5)

    cur = db.cursor()
    cur.execute("INSERT INTO steam_guard_codes (email, username, code) VALUES (%s, %s, %s);", (email, username, code))
    db.commit()
    cur.close()

def fetch_codes():
    client = Gmail()
    client.login(sys.argv[1], email_password)
    mails = client.inbox().mail(unread=True, sender="noreply@steampowered.com")

    for entry in mails:
        entry.fetch()

        if 'need to complete the process:' not in entry.body:
            continue

        entry.read()
        
        # First, find the username this went too
        username = re.findall("Dear (.*),", entry.body)[0]

        # Label this as a proper steam-guard code
        entry.add_label("Codes")

        # Grab the actual steam-guard code
        _, data = entry.body.split("need to complete the process:")
        code = data.strip().split("\n", 1)[0].strip()

        store_code(entry.to, username, code)

    client.logout()

while True:
    try:
        fetch_codes()
        time.sleep(15)
    except KeyboardInterrupt:
        break
    except Exception as e:
        print "Error: %s" % e
        time.sleep(30)

db.close()

