#!/bin/bash

(crontab -l -u root; echo "* * * * * echo foi >> home/testeCron") | crontab
cron -f
#(crontab -l -u root; echo "0 0 * * * ./utils/backup.sh") | crontab
