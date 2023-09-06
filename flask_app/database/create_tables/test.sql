CREATE TABLE IF NOT EXISTS `test` (
`test_id`   int(11)      NOT NULL auto_increment COMMENT 'the transaction id',
`user_id`   varchar(10)  NOT NULL COMMENT 'the user id of the transaction',
`player_id` varchar(100) NOT NULL COMMENT 'the player id of the transaction',
`pass`      json         NOT NULL COMMENT 'pass stats',
`rush`      json         NOT NULL COMMENT 'rush stats',
`rec`       json         NOT NULL COMMENT 'rec stats',
PRIMARY KEY (`test_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT='Contains transaction information';