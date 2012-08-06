SHELL=/bin/bash

deploy-web:
	sudo killall -q python || true
	sudo nohup python main.py >> /dev/null 2>> /dev/null < /dev/null &

reset-database:
	mysql -u root -proot root < etc/schema.sql
