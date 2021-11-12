CREATE TABLE `common_config` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `create_time` datetime(6) NOT NULL COMMENT '创建时间',
  `update_time` datetime(6) NOT NULL COMMENT '更新时间',
  `server` varchar(50) NOT NULL COMMENT '所属服务名称',
  `name` varchar(50) NOT NULL COMMENT '配置名称',
  `value` longtext NOT NULL COMMENT '配置内容',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='配置表';