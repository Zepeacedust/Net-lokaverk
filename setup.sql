create database 0903032790_Users;
use 0903032790_Users;
create table users (
    username varchar(128) primary key,
    pass char(192)
);
create table posts (
    Id int auto_increment primary key not null,
    title varchar(100),
    body varchar(2000),
    author varchar(128),
    foreign key(author) references users(username)
);
insert into posts (Id, title, body, author) values (
	0,"gronk", "hello bretheren", "Grurkey"
);
