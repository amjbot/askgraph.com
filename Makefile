SHELL=/bin/bash

deploy-web:
	sudo killall -q python || true
	sudo nohup python main.py >> log/out.log 2>> log/err.log < /dev/null &

reset-database:
	mysql -u root -proot root < etc/schema.sql

tail-log:
	tail -f log/out.log

tail-err:
	tail -f log/err.log
