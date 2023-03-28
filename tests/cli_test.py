from subprocess import check_output

path = 'https://github.com/Vi-812/git_check_alive'

return_json = check_output('python ..\cli.py ' + path, shell=True).decode()
print(return_json)
