CREATE TABLE icons (
	id integer primary key autoincrement,
	title text not null unique,
	uri text not null,
	active boolean default true
);
