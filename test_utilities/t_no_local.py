import os
import requests
import random
from datetime import datetime
from loguru import logger
from dotenv import load_dotenv
load_dotenv()

logger.add(
    'no_local_test.log',
    format='{time:DD-MM HH:mm} {message}',
    level='INFO',
    )


url = 'http://51.68.189.155/api'
token = os.getenv('TOKEN')
while True:
    time = datetime.utcnow()
    test_repo = [
        'https://github.com/dbeaver/dbeaver',
        'https://github.com/kubernetes/kubernetes',
        'https://github.com/apache/spark',
        'github.com/Microsoft/vscode',
        'github.com/NixOS/nixpkgs',
        'github.com/rust-lang/rust',
        'github.com/firehol/blocklist-ipsets',
        'github.com/openshift/origin',
        'github.com/ansible/ansible',
        'github.com/Automattic/wp-calypso',
        'github.com/dotnet/corefx',
        'https://github.com/dotnet/roslyn',
        'github.com/nodejs/node',
        'github.com/tensorflow/tensorflow',
        'github.com/freeCodeCamp/freeCodeCamp',
        'github.com/tgstation/tgstation',
        'github.com/apple/swift',
        'github.com/elastic/elasticsearch',
        'github.com/moby/moby',
        'github.com/cockroachdb/cockroach',
        'github.com/jlippold/tweakCompatible',
    ]

    random_repo = random.randint(0, len(test_repo)-1)
    # random_repo = 5

    json = {
        'token': token,
        'repository_path': test_repo[random_repo]
    }

    print(random_repo, json['repository_path'])
    logg_repo = str(random_repo) + ' => ' + json['repository_path']

    response = requests.post(url=url, json=json)
    print(response.status_code, response.text)
    if response.status_code != 200:
        logger.info(logg_repo + ' ' + str(response.status_code))
    time = datetime.utcnow() - time
    if time.seconds > 2:
        break
