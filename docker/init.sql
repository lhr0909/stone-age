-- sasql_query reads SELECT * column 1 as the password: preserve this order.
CREATE TABLE IF NOT EXISTS user_table (
  Name VARCHAR(32) CHARACTER SET ascii COLLATE ascii_bin PRIMARY KEY,
  Pass VARCHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  RegTime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  Path VARCHAR(64) NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS user_lock (
  Name VARCHAR(64) CHARACTER SET ascii COLLATE ascii_bin PRIMARY KEY
);
-- Local development account. The old protocol compares plaintext passwords.
INSERT IGNORE INTO user_table (Name, Pass) VALUES ('player', 'stoneage');
