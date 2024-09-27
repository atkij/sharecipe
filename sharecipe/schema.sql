DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS verify;
DROP TABLE IF EXISTS profile;
DROP TABLE IF EXISTS follower;
DROP TABLE IF EXISTS recipe;
DROP TABLE IF EXISTS rating;
DROP TABLE IF EXISTS photo;
DROP TABLE IF EXISTS favourite;
DROP TABLE IF EXISTS comment;
DROP TABLE IF EXISTS reply;

CREATE TABLE user (
	user_id INTEGER NOT NULL PRIMARY KEY,
	email TEXT NOT NULL UNIQUE CHECK (LENGTH(email) <= 256),
	password TEXT NOT NULL,
	verified INTEGER NOT NULL DEFAULT 0,
	created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
	last_login TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE verify (
	user_id INTEGER NOT NULL PRIMARY KEY,
	code TEXT NOT NULL,
	expires TEXT NOT NULL,
	FOREIGN KEY (user_id) REFERENCES user (user_id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE profile (
	user_id INTEGER NOT NULL PRIMARY KEY,
	name TEXT NOT NULL CHECK (LENGTH(name) <= 56),
	bio TEXT CHECK (LENGTH(bio) <= 400),
	picture TEXT,
	FOREIGN KEY (user_id) REFERENCES user (user_id) ON UPDATE CASCADE ON DELETE CASCADE
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
	FOREIGN KEY (user_id) REFERENCES user (user_id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE rating (
	user_id INTEGER NOT NULL,
	recipe_id INTEGER NOT NULL,
	rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
	FOREIGN KEY (user_id) REFERENCES user (user_id) ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY (recipe_id) REFERENCES recipe (recipe_id) ON UPDATE CASCADE ON DELETE CASCADE,
	PRIMARY KEY (user_id, recipe_id)
);

CREATE TABLE photo (
	photo_id INTEGER NOT NULL PRIMARY KEY,
	post_id INTEGER NOT NULL,
	photo TEXT NOT NULL,
	FOREIGN KEY (post_id) REFERENCES post (post_id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE favourite (
	user_id INTEGER NOT NULL,
	recipe_id INTEGER NOT NULL,
	FOREIGN KEY (user_id) REFERENCES user(user_id) ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY (recipe_id) REFERENCES recipe(recipe_id) ON UPDATE CASCADE ON DELETE CASCADE,
	PRIMARY KEY (user_id, recipe_id)
);

CREATE TABLE comment (
	comment_id INTEGER NOT NULL PRIMARY KEY,
	user_id INTEGER NOT NULL,
	recipe_id INTEGER NOT NULL,
	body TEXT NOT NULL,
	created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (user_id) REFERENCES user(user_id) ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY (recipe_id) REFERENCES recipe(recipe_id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE reply (
	comment_id INTEGER NOT NULL,
	reply_id INTEGER NOT NULL,
	FOREIGN KEY (comment_id) REFERENCES comment(comment_id) ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY (reply_id) REFERENCES comment(comment_id) ON UPDATE CASCADE ON DELETE CASCADE,
	PRIMARY KEY (comment_id, reply_id)
);

CREATE VIEW profile_view
AS
SELECT profile.user_id, profile.name, profile.bio, profile.picture, user.created AS joined, user.last_login AS active
FROM profile
INNER JOIN user ON profile.user_id = user.user_id;