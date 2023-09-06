CREATE TABLE IF NOT EXISTS `playerData` (
`data_id`         int(11)  	   NOT NULL auto_increment	  COMMENT 'the id of this user',
`player_id`       json  NOT NULL                   COMMENT 'the role of the user; options include: owner and guest',
`pass`         varchar(100) NOT NULL            		  COMMENT 'the email',
`password`        varchar(256) NOT NULL                   COMMENT 'the password',
`token`           int(11)       DEFAULT NULL              COMMENT 'The token amount',




PRIMARY KEY (`data_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT='Contains site user information';
