INSERT INTO user (username, password, name, bio, email) VALUES ('test', 'scrypt:16384:8:1$8986dc0c476fcb2cf74f50f3a1958df5$1e0f3e807a5b590c8f59a2565316ffc4f64993f636ceaafdd9a3992c9502f41ce8cd040e40af8e11c9a0b8ccb3d4de1b6f2950a8121b7fcf31217e7cc9e0fe55', 'Test', 'This is the test account.', 'user1@example.com');
INSERT INTO user (username, password, name, bio, email) VALUES ('other', 'scrypt:16384:8:1$e73fdda4089da790062069278d3059d7$baf2bf740739bec38ae35f1b5b9490dfee5fbf368dca4c6bb245b0e26275878cf57989cfec2a8dcaa0d4360834982e023ad8444f3ac4c3bdea5330bc97a2be67', 'Other', 'This is the other account.', 'user2@example.com');

INSERT INTO follower (user_id, follower_id) VALUES (2, 1);

INSERT INTO recipe (user_id, title, ingredients, method, vegetarian) VALUES (1, 'Recipe 1', 'Ingredients', 'Method', 1);
INSERT INTO recipe (user_id, title, ingredients, method, vegetarian) VALUES (2, 'Recipe 2', 'Ingredients', 'Method', 0);
