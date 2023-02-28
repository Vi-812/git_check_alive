import sys
import os
import argparse
import asyncio
import backend.database as db
from dotenv import load_dotenv
load_dotenv()

token = os.getenv('TOKEN')

try:
    parser = argparse.ArgumentParser()
    parser.add_argument('repository_path', nargs='?')
    args = parser.parse_args()
except:
    print('An error occurred, too many arguments were passed')
    print('Pass the link or "owner/repository_name" as an argument')
    print('"https://github.com/Vi-812/git_check_alive" or "vi-812/git_check_alive"')
    sys.exit()

if not args.repository_path:
    print('Pass the link or "owner/repository_name" as an argument')
    print('"https://github.com/Vi-812/git_check_alive" or "vi-812/git_check_alive"')
    sys.exit()

instance_dbh = db.DataBaseHandler()
resp_json, code = asyncio.run(instance_dbh.get_report(repository_path=args.repository_path, token=token))
print(resp_json)
