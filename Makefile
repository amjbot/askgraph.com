SHELL=/bin/bash

deploy-web:
	#sudo nohup killall -q python > /dev/null 2> /dev/null < /dev/null
	sudo nohup python main.py >> /dev/null 2>> /dev/null < /dev/null &

reset-database:
	mysql -u root -proot root < etc/schema.sql
