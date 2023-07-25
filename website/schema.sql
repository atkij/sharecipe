
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS follower;
DROP TABLE IF EXISTS recipe_category;
DROP TABLE IF EXISTS recipe;

CREATE TABLE user (
	user_id INTEGER NOT NULL PRIMARY KEY,
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
	FOREIGN KEY (user_id) REFERENCES user (id) ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY (follower_id) REFERENCES user (id) ON UPDATE CASCADE ON DELETE CASCADE,
	PRIMARY KEY (user_id, follower_id)
);

CREATE TABLE recipe_category (
	category_id INTEGER NOT NULL PRIMARY KEY,
	category TEXT NOT NULL
);

CREATE TABLE recipe (
	recipe_id INTEGER NOT NULL PRIMARY KEY,
	user_id INTEGER NOT NULL,
	category_id INTEGER,
	ingredients TEXT NOT NULL,
	method TEXT NOT NULL,
	time INTEGER NOT NULL CHECK (time > 0 AND time < 6),
	difficulty INTEGER NOT NULL CHECK (difficulty > 0 AND difficulty < 6),
	servings INTEGER NOT NULL CHECK (servings > 0),
	tags TEXT,
	FOREIGN KEY (user_id) REFERENCES user (user_id) ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY (category_id) REFERENCES recipe_category (category_id) ON UPDATE CASCADE ON DELETE SET NULL
);
