DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS permission;

CREATE TABLE user (
	id INTEGER NOT NULL PRIMARY KEY,
	username TEXT NOT NULL UNIQUE,
	password TEXT NOT NULL,
	permissions INTEGER NOT NULL,
	created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
	last_login TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE follower (
	user_id INTEGER NOT NULL,
	follower_id INTEGER NOT NULL,
	CHECK (user_id != follower_id),
	FOREIGN KEY (user_id) REFERENCES user (id),
	FOREIGN KEY (follower_id) REFERENCES user (id),
	PRIMARY KEY (user_id, follower_id)
)