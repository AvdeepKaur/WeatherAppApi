DROP TABLE IF EXISTS users;
CREATE TABLE user_favorites (
    user_id INTEGER REFERENCES users(user_id),
    location_id TEXT,
    location_name TEXT,
    PRIMARY KEY (user_id, location_id)
);