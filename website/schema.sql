DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS follower;
DROP TABLE IF EXISTS recipe_category;
DROP TABLE IF EXISTS recipe;

CREATE TABLE user (
	user_id INTEGER NOT NULL PRIMARY KEY,
	username TEXT NOT NULL UNIQUE CHECK (LENGTH(username) >= 3 AND LENGTH(username) <= 36),
	password TEXT NOT NULL CHECK (LENGTH(password) >= 8 AND LENGTH(password) <= 256),
	created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
	last_login TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE follower (
	user_id INTEGER NOT NULL,
	follower_id INTEGER NOT NULL,
	CHECK (user_id != follower_id),
	FOREIGN KEY (user_id) REFERENCES user (user_id) ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY (follower_id) REFERENCES user (user_id) ON UPDATE CASCADE ON DELETE CASCADE,
	PRIMARY KEY (user_id, follower_id)
);

CREATE TABLE recipe (
	recipe_id INTEGER NOT NULL PRIMARY KEY,
	user_id INTEGER NOT NULL,
	title TEXT NOT NULL CHECK (LENGTH(title) <= 50),
	description TEXT CHECK (LENGTH(description) <= 400),
	ingredients TEXT NOT NULL CHECK (LENGTH(ingredients) <= 1000),
	method TEXT NOT NULL CHECK (LENGTH(method) <= 4000),
	time INTEGER CHECK (time > 0),
	difficulty INTEGER CHECK (difficulty > 0 AND difficulty <= 5),
	servings INTEGER CHECK (servings > 0),
	tags TEXT CHECK (LENGTH(tags) <= 100),
	created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (user_id) REFERENCES user (user_id) ON UPDATE CASCADE ON DELETE CASCADE
);
