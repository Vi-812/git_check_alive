cd git_check_alive
git stash
git pull origin main
sudo rm app/logs/info.log app/logs/warning.log app/logs/error.log tests/log_info.log tests/log_warn.log tests/log_err.log app/db/repo.db -f
screen -r server
