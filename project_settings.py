import os

Lines = open('.env', 'r').readlines()

for line in Lines:
    line = line.strip()
    os.environ[line[:line.find("=")]] = line[line.find("=") + 1:]
TOKEN = os.environ['TOKEN']
# The string list of chat id is turned into a list object
ADMINS = [_.strip() for _ in os.environ['ADMINS'].split(',')]
