DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS follower;
DROP TABLE IF EXISTS recipe;
DROP TABLE IF EXISTS post;

CREATE TABLE user (
	user_id INTEGER NOT NULL PRIMARY KEY,
	username TEXT NOT NULL UNIQUE CHECK (LENGTH(username) >= 3 AND LENGTH(username) <= 36),
	password TEXT NOT NULL CHECK (LENGTH(password) >= 8 AND LENGTH(password) <= 256),
	name TEXT CHECK (LENGTH(name) <= 56),
	bio TEXT CHECK (LENGTH(bio) <= 400),
	picture TEXT,
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
	title TEXT NOT NULL CHECK (LENGTH(title) <= 100),
	photo TEXT,
	description TEXT CHECK (LENGTH(description) <= 400),
	ingredients TEXT NOT NULL CHECK (LENGTH(ingredients) <= 1000),
	method TEXT NOT NULL CHECK (LENGTH(method) <= 4000),
	time INTEGER CHECK (time > 0),
	difficulty INTEGER CHECK (difficulty > 0 AND difficulty <= 3),
	servings INTEGER CHECK (servings > 0),
	vegetarian INTEGER NOT NULL CHECK (vegetarian IN (0, 1)),
	tags TEXT CHECK (LENGTH(tags) <= 100),
	created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated TEXT,
	FOREIGN KEY (user_id) REFERENCES user (user_id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE post (
	post_id INTEGER NOT NULL PRIMARY KEY,
	user_id INTEGER NOT NULL,
	title TEXT NOT NULL CHECK (LENGTH(title) <= 100),
	body TEXT NOT NULL CHECK (LENGTH(body) <= 4000),
	created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated TEXT,
	FOREIGN KEY (user_id) REFERENCES user (user_id) ON UPDATE CASCADE ON DELETE CASCADE
);

/*
CHANGES

 - post table (new)
 - firstname in user (new)
 - lastname in user (new)
 - bio in user (new)
*/
