cd git_check_alive
git stash
git pull origin main
sudo rm log_info.log log_warn.log log_err.log tests/log_info.log tests/log_warn.log tests/log_err.log backend/db/repo.db -f
screen -r server
ps au
