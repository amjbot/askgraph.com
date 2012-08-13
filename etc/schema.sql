SET SESSION storage_engine = "InnoDB";
SET SESSION time_zone = "+0:00";
ALTER DATABASE CHARACTER SET "utf8";

CREATE TABLE IF NOT EXISTS requests (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARBINARY(30) NOT NULL DEFAULT '',
    request VARBINARY(3000) NOT NULL DEFAULT '',
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS document_headers (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    dataset VARBINARY(100) NOT NULL UNIQUE,
    source VARBINARY(300) NOT NULL DEFAULT '',
    sourcename VARBINARY(100) NOT NULL DEFAULT '',
    col0 VARBINARY(20) NOT NULL DEFAULT '',
    col1 VARBINARY(20) NOT NULL DEFAULT '',
    col2 VARBINARY(20) NOT NULL DEFAULT '',
    col3 VARBINARY(20) NOT NULL DEFAULT '',
    col4 VARBINARY(20) NOT NULL DEFAULT '',
    col5 VARBINARY(20) NOT NULL DEFAULT '',
    col6 VARBINARY(20) NOT NULL DEFAULT '',
    col7 VARBINARY(20) NOT NULL DEFAULT '',
    col8 VARBINARY(20) NOT NULL DEFAULT '',
    col9 VARBINARY(20) NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS documents (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    dataset VARBINARY(100) NOT NULL,
    col0 VARBINARY(200) NOT NULL DEFAULT '',
    col1 VARBINARY(200) NOT NULL DEFAULT '',
    col2 VARBINARY(200) NOT NULL DEFAULT '',
    col3 VARBINARY(200) NOT NULL DEFAULT '',
    col4 VARBINARY(200) NOT NULL DEFAULT '',
    col5 VARBINARY(200) NOT NULL DEFAULT '',
    col6 VARBINARY(200) NOT NULL DEFAULT '',
    col7 VARBINARY(200) NOT NULL DEFAULT '',
    col8 VARBINARY(200) NOT NULL DEFAULT '',
    col9 VARBINARY(200) NOT NULL DEFAULT '',
    KEY(dataset)
);

CREATE TABLE IF NOT EXISTS queue (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    state ENUM('open','active','complete','confirmed'),
    route VARBINARY(200) NOT NULL DEFAULT '',
    delay TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    argument VARBINARY(2000) NOT NULL DEFAULT ''
);
