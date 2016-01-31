#!/usr/bin/env python
import sys, getpass, time, argparse, psycopg2
from crypt import encrypt

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", help="The password file")
parser.add_argument("-n", "--name", help="The name format", default="csgoebot%s")
parser.add_argument("-s", "--start", help="The start number", default=0)
args = parser.parse_args()

def open_database_connection(pw):
    return psycopg2.connect("host=104.171.118.100 port=50432 dbname=emporium user=emporium password=%s" % pw)

if len(sys.argv) <= 1:
    print "Usage: ./guardmail.py <accounts file>"
    sys.exit(1)

db_password = getpass.getpass("DB Password > ")
enc_password = getpass.getpass("PW Encryption Password > ")
db = open_database_connection(db_password)

ADD_QUERY = """
INSERT INTO accounts (username, password, status, active) VALUES (%s, %s, 'AVAIL', true);
"""

def add_account(name, password):
    cur = db.cursor()
    cur.execute(ADD_QUERY, (name, encrypt(enc_password, password)))
    db.commit()
    cur.close()

def import_accounts(f, name_format, start):
    for line in f.readlines():
        add_account(name_format % start, line.strip())
        start += 1

import_accounts(open(args.file), args.name, int(args.start))

db.close()

