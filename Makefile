SHELL=/bin/bash

restart:
	sudo supervisorctl restart all

status:
	sudo supervisorctl status all

stop:
	sudo supervisorctl stop all

backup-database:
	mysqldump root -u root -proot > .backup.sql

load-database:
	mysql -u root -proot root < .backup.sql

reset-database:
	mysql -u root -proot root < etc/schema.sql

tail-log:
	sudo tail -1000 /var/log/supervisor/askgraph-stdout*.log

tail-err:
	sudo tail -1000 /var/log/supervisor/askgraph-stderr*.log
