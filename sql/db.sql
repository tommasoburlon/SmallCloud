CREATE DATABASE forum;
USE forum;

DROP TABLE IF EXISTS user;
CREATE TABLE user(
	id       INT NOT NULL AUTO_INCREMENT,
	username VARCHAR(255),
	password VARCHAR(255),
	PRIMARY KEY (id)
);

DROP TABLE IF EXISTS thread;
CREATE TABLE thread(
	id       INT NOT NULL AUTO_INCREMENT,
	user_id  INT,
	title    VARCHAR(255),
	PRIMARY KEY (id)
);

DROP TABLE IF EXISTS comment;
CREATE TABLE comment(
	id         INT NOT NULL AUTO_INCREMENT,
	thread_id  INT,
	user_id    INT,
	body       VARCHAR(1024),
	postDate   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (id)
);
