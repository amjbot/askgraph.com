SHELL=/bin/bash

restart:
	sudo supervisorctl restart all

status:
	sudo supervisorctl status all

stop:
	sudo supervisorctl stop all

db:
	mysql -u root -proot root

restore-database:
	./scripts/download_s3.py backups/daily.sql.tar.gz
	tar -xzf daily.sql.tar.gz
	mysql -u root -proot root < .backup.sql
	rm daily.sql.tar.gz
	rm .backup.sql

reset-database:
	mysql -u root -proot root < etc/schema.sql

tail-log:
	sudo tail -1000 /var/log/supervisor/askgraph-stdout*.log

tail-err:
	sudo tail -1000 /var/log/supervisor/askgraph-stderr*.log
