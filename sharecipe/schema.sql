DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS profile;

DROP TABLE IF EXISTS recipe;
DROP TABLE IF EXISTS recipe_part;
DROP TABLE IF EXISTS recipe_ingredient;
DROP TABLE IF EXISTS recipe_instruction;
DROP TABLE IF EXISTS recipe_photo;
DROP TABLE IF EXISTS recipe_favourite;

DROP TABLE IF EXISTS collection;
DROP TABLE IF EXISTS collection_item;
DROP TABLE IF EXISTS collection_photo;
DROP TABLE IF EXISTS collection_favourite;

DROP VIEW IF EXISTS profile_view;

CREATE TABLE user (
	id INTEGER NOT NULL PRIMARY KEY,
	email TEXT NOT NULL UNIQUE CHECK (LENGTH(email) <= 256),
	password TEXT NOT NULL,
	verified INTEGER NOT NULL DEFAULT 0,
	created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
	last_login TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE profile (
	id INTEGER NOT NULL PRIMARY KEY,
	name TEXT NOT NULL CHECK (LENGTH(name) <= 56),
	bio TEXT CHECK (LENGTH(bio) <= 400),
	picture TEXT,
	FOREIGN KEY (id) REFERENCES user (id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE recipe (
	id INTEGER NOT NULL PRIMARY KEY,
	user_id INTEGER NOT NULL,

	title TEXT NOT NULL,
	description TEXT,

	prepare INTEGER,
	cook INTEGER,
	serves TEXT,
	vegetarian INTEGER NOT NULL,

	tags TEXT,
	created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

	FOREIGN KEY (user_id) REFERENCES user (id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE recipe_part (
	id INTEGER NOT NULL PRIMARY KEY,
	recipe_id INTEGER NOT NULL,

	position INTEGER,
	name TEXT,
	
	FOREIGN KEY (recipe_id) REFERENCES recipe (id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE recipe_ingredient (
	id INTEGER NOT NULL PRIMARY KEY,
	part_id INTEGER NOT NULL,

	position INTEGER NOT NULL,
	ingredient TEXT NOT NULL,

	FOREIGN KEY (part_id) REFERENCES recipe_part (id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE recipe_instruction (
	id INTEGER NOT NULL PRIMARY KEY,
	recipe_id INTEGER NOT NULL,

	position INTEGER NOT NULL,
	instruction TEXT NOT NULL,

	FOREIGN KEY (recipe_id) REFERENCES recipe (id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE recipe_photo (
	id INTEGER NOT NULL PRIMARY KEY,
	recipe_id INTEGER NOT NULL,

	position INTEGER NOT NULL,
	photo_uri TEXT NOT NULL,

	FOREIGN KEY (recipe_id) REFERENCES recipe (id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE recipe_favourite (
	user_id INTEGER NOT NULL,
	recipe_id INTEGER NOT NULL,

	FOREIGN KEY (user_id) REFERENCES user (id) ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY (recipe_id) REFERENCES recipe (id) ON UPDATE CASCADE ON DELETE CASCADE,
	PRIMARY KEY (user_id, recipe_id)
);

CREATE TABLE collection (
	id INTEGER NOT NULL PRIMARY KEY,
	user_id INTEGER NOT NULL,

	name TEXT NOT NULL,
	description TEXT,

	FOREIGN KEY (user_id) REFERENCES user (id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE collection_item (
	collection_id INTEGER NOT NULL,
	recipe_id INTEGER NOT NULL,

	position INTEGER NOT NULL,

	FOREIGN KEY (collection_id) REFERENCES collection (id) ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY (recipe_id) REFERENCES recipe (id) ON UPDATE CASCADE ON DELETE CASCADE,
	PRIMARY KEY (collection_id, recipe_id)
);

CREATE TABLE collection_photo (
	id INTEGER NOT NULL PRIMARY KEY,
	collection_id INTEGER NOT NULL,

	position INTEGER NOT NULL,
	photo_uri TEXT NOT NULL,

	FOREIGN KEY (collection_id) REFERENCES collection (id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE collection_favourite (
	user_id INTEGER NOT NULL,
	collection_id INTEGER NOT NULL,

	FOREIGN KEY (user_id) REFERENCES user (id) ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY (collection_id) REFERENCES collection (id) ON UPDATE CASCADE ON DELETE CASCADE,
	PRIMARY KEY (user_id, collection_id)
);

CREATE VIEW profile_view
AS
SELECT profile.user_id, profile.name, profile.bio, profile.picture, user.created AS joined, user.last_login AS active
FROM profile
INNER JOIN user ON profile.user_id = user.id;