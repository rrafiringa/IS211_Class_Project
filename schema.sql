PRAGMA FOREIGN_KEYS = ON;

-- Login Table
DROP TABLE IF EXISTS users;
CREATE TABLE IF NOT EXISTS users (
  username VARCHAR PRIMARY KEY NOT NULL UNIQUE,
  fname    VARCHAR NOT NULL,
  lname    VARCHAR NOT NULL,
  password VARCHAR,
  email    VARCHAR
);

-- Blog Entry
DROP TABLE IF EXISTS posts;
CREATE TABLE IF NOT EXISTS posts (
  pid      INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
  ts       DATETIME NOT NULL DEFAULT (datetime('now')),
  title    VARCHAR  NOT NULL,
  post     VARCHAR,
  state    INTEGER DEFAULT 1,
  username VARCHAR REFERENCES users (username) ON DELETE CASCADE
);

DROP INDEX IF EXISTS posts_idx;
CREATE INDEX IF NOT EXISTS posts_idx ON posts (pid);

INSERT INTO users (username,
                   fname,
                   lname,
                   password,
                   email) VALUES ('admin',
                                  'John',
                                  'Admin',
                                  'password',
                                  'admin@blogger.com')


