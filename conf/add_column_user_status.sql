-- schema.sql

use awesome;
grant alter on awesome.* to 'www-data'@'localhost' identified by 'www-data';

alter table users add column status int default 0;
alter table users add column confirm varchar(50);