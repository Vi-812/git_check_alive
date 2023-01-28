from subprocess import check_output

testing = False

if not testing:
    repository_path = [
        'https://github.com/Vi-812/git_check_alive',
        'https://github.com/pallets/flask',
    ]
else:
    repository_path = [
        'zero',
        'vi-812/git_',
        'vi-812/empty',
        'vi-812/git_check_alive',
        'https://github.com/pallets/flask',
        'facebook/jest',
        'https://github.com/dbeaver/dbeaver',
    ]

for path in repository_path:
    return_json = check_output('python ..\cli.py ' + path, shell=True).decode()
    print(return_json)