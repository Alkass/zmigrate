create table avatars (
	id integer primary key autoincrement,
	title text not null unique,
	uri text not null,
	active boolean default true
);

create table users (
	id integer primary key autoincrement,
	username text not null unique,
	password text not null,
	avatar_id integer references avatars(id) default null,
	active boolean default true
);


