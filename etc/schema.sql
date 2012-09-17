SET SESSION storage_engine = "InnoDB";
SET SESSION time_zone = "+0:00";
ALTER DATABASE CHARACTER SET "utf8";

DROP TABLE IF EXISTS requests;
CREATE TABLE IF NOT EXISTS requests (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    email VARBINARY(500) NOT NULL,
    request TEXT NOT NULL,
    bid DOUBLE,
    bid_currency NOT NULL DEFAULT 'USD',
    previous DATETIME,
    period DATETIME,
    KEY(email)
);
