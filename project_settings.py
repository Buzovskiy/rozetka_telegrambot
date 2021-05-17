import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent

Lines = open(BASE_DIR / '.env', 'r').readlines()

for line in Lines:
    line = line.strip()
    os.environ[line[:line.find("=")]] = line[line.find("=") + 1:]
TOKEN = os.environ['TOKEN']
# The string list of chat id is turned into a list object
ADMINS = [_.strip() for _ in os.environ['ADMINS'].split(',')]
PAGE_LINK = os.environ['PAGE_LINK']

