-- schema.sql

use awesome;
grant alter on awesome.* to 'www-data'@'localhost' identified by 'www-data';

create table reply (
    `id` varchar(50) not null,
    `comment_id` varchar(50) not null,
    `user_id` varchar(50) not null,
    `reply_user_id` varchar(50) not null,
    `user_name` varchar(50) not null,
    `user_image` varchar(500) not null,
    `content` mediumtext not null,
    `created_at` real not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;