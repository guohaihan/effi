CREATE TABLE `reports_jira_version` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `create_time` datetime(6) NOT NULL COMMENT '创建时间',
  `update_time` datetime(6) NOT NULL COMMENT '更新时间',
  `name` varchar(255) NOT NULL COMMENT '版本名称',
  `description` varchar(255) DEFAULT NULL COMMENT '版本描述',
  `released` tinyint(1) NOT NULL COMMENT '是否发布',
  `start_date` date DEFAULT NULL,
  `release_date` date DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1529 DEFAULT CHARSET=utf8 COMMENT='jira version';