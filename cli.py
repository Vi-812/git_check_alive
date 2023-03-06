import sys
import os
import argparse
import asyncio
from dto.received_request import ReceivedRequest
import backend.database as db
from dto.json_preparation import final_json_preparation
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

rec_request = ReceivedRequest(url='CLI request', repo_path=args.repository_path, token=token)
instance_dbh = db.DataBaseHandler()
resp_json = asyncio.run(instance_dbh.get_report(rec_request=rec_request))
resp_json = final_json_preparation(resp_json=resp_json)
print(resp_json)
