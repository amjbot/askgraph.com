show-database:
	mysqldump root -u root -proot --tables noisebot_input noisebot_output

load-database:
	mysql -u root -proot root < .backup.sql

reset-database:
	mysql -u root -proot root < schema.sql
