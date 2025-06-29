#!/bin/zsh
nohup python3 ~/Code/web-scrape/init.py > ~/Code/web-scrape/output.log 2>&1 &

# python3 ~/Code/web-scrape/init.py

# check bg process
# ps aux | grep init.py