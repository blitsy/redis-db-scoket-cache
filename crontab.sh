@reboot python /home/pi/redis-db-scoket-cache/socket-server.py >> /home/pi/server_out.log 2>&1

* * * * * sh /home/pi/cron.sh >> /home/pi/data_cache_log.out 2>&1
