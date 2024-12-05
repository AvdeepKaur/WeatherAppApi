DROP TABLE IF EXISTS users;
CREATE TABLE users (
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    name TEXT NOT NULL,
    cityfavone TEXT DEFAULT NULL,
    cityfavtwo TEXT DEFAULT NULL,
    cityfavthree TEXT DEFAULT NULL
);