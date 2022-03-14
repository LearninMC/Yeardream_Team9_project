CREATE TABLE if not exists `post` (
  `id` int NOT NULL AUTO_INCREMENT,
  `author` varchar(256) NOT NULL,
  `content` text NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ;

CREATE TABLE if not exists `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` varchar(100) NOT NULL,
  `user_pw` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
);
