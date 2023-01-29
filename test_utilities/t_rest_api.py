import os
import requests
from dotenv import load_dotenv
load_dotenv()

mega_test = True

url = 'http://localhost:8080/api'
token = os.getenv('TOKEN')

if not mega_test:
    testing = [
        'vi-812/empty',
        'vi-812/git_check_alive',
        'https://github.com/pallets/flask',
    ]
else:
    testing = [
        'zero',
        'vi-812/git_',
        'vi-812/empty',
        'vi-812/git_check_alive',
        'https://github.com/pallets/flask',
        'facebook/jest',
    ]
    yyy = [
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

for test in testing:
    body = {
        'token': token,
        'repository_path': test
    }
    response = requests.post(url=url, json=body)
    print(response.status_code, response.text)
