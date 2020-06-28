CREATE TABLE users (
	id serial primary key,
	username text not null unique
);
