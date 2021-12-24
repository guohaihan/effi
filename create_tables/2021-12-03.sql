
CREATE TABLE `reports_item_reports` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `create_time` datetime(6) NOT NULL COMMENT '创建时间',
  `update_time` datetime(6) NOT NULL COMMENT '更新时间',
  `name` varchar(50) NOT NULL COMMENT '迭代名称',
  `type` varchar(11) NOT NULL,
  `content` varchar(200) NOT NULL COMMENT '需求内容',
  `domain_influence` varchar(200) DEFAULT NULL COMMENT '影响域',
  `start_time` date NOT NULL COMMENT '开始时间',
  `end_time` date NOT NULL COMMENT '上线时间',
  `total_day` decimal(3,1) NOT NULL COMMENT '总工作日',
  `rf_day` decimal(3,1) NOT NULL COMMENT '研发工作日',
  `test_day` decimal(3,1) NOT NULL COMMENT '测试工作日',
  `acceptance_day` decimal(3,1) NOT NULL COMMENT '验收工作日',
  `group` int NOT NULL COMMENT '研发组数',
  `risk` varchar(255) DEFAULT NULL COMMENT '风险内容',
  `legacy` varchar(255) DEFAULT NULL COMMENT '遗留问题',
  `feel` longtext COMMENT '整体感受',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8 COMMENT='果之迭代报告';

CREATE TABLE `reports_bug_class` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `function_error` int NOT NULL COMMENT '功能错误',
  `function_optimize` int NOT NULL COMMENT '功能优化',
  `interface_optimize` int NOT NULL COMMENT '界面优化',
  `performance` int NOT NULL COMMENT '性能优化',
  `safety` int NOT NULL COMMENT '安全问题',
  `rd` int NOT NULL COMMENT '后端bug',
  `fe` int NOT NULL COMMENT '前端bug',
  `item_reports_id` int NOT NULL COMMENT '迭代报告id',
  PRIMARY KEY (`id`),
  UNIQUE KEY `item_reports_id` (`item_reports_id`),
  CONSTRAINT `reports_bug_class_item_reports_id_70950493_fk_reports_i` FOREIGN KEY (`item_reports_id`) REFERENCES `reports_item_reports` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8 COMMENT='bug分类表';


CREATE TABLE `reports_item_reports` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `create_time` datetime(6) NOT NULL COMMENT '创建时间',
  `update_time` datetime(6) NOT NULL COMMENT '更新时间',
  `name` varchar(50) NOT NULL COMMENT '迭代名称',
  `type` varchar(11) NOT NULL,
  `content` varchar(200) NOT NULL COMMENT '需求内容',
  `domain_influence` varchar(200) DEFAULT NULL COMMENT '影响域',
  `start_time` date NOT NULL COMMENT '开始时间',
  `end_time` date NOT NULL COMMENT '上线时间',
  `total_day` decimal(3,1) NOT NULL COMMENT '总工作日',
  `rf_day` decimal(3,1) NOT NULL COMMENT '研发工作日',
  `test_day` decimal(3,1) NOT NULL COMMENT '测试工作日',
  `acceptance_day` decimal(3,1) NOT NULL COMMENT '验收工作日',
  `group` int NOT NULL COMMENT '研发组数',
  `risk` varchar(255) DEFAULT NULL COMMENT '风险内容',
  `legacy` varchar(255) DEFAULT NULL COMMENT '遗留问题',
  `feel` longtext COMMENT '整体感受',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8 COMMENT='果之迭代报告';


CREATE TABLE `reports_score` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `product_score` decimal(3,2) NOT NULL COMMENT 'PM改动需求得分',
  `rf_delay` decimal(3,2) NOT NULL COMMENT '故事交付延期得分',
  `todo` decimal(3,2) NOT NULL COMMENT '冒烟通过率得分',
  `unit_bug` decimal(3,2) NOT NULL COMMENT '单位bug数',
  `finish_story_day` decimal(3,2) NOT NULL COMMENT '每天完成的故事点',
  `item_reports_id` int NOT NULL COMMENT '迭代报告id',
  `total` decimal(3,2) NOT NULL COMMENT '迭代得分',
  PRIMARY KEY (`id`),
  UNIQUE KEY `item_reports_id` (`item_reports_id`),
  CONSTRAINT `reports_score_item_reports_id_4045d69c_fk_reports_i` FOREIGN KEY (`item_reports_id`) REFERENCES `reports_item_reports` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8 COMMENT='分值表';


CREATE TABLE `reports_story` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `content` varchar(255) NOT NULL COMMENT '用户故事',
  `assess_length` decimal(3,1) NOT NULL COMMENT '评估时长',
  `product_delays` decimal(3,1) NOT NULL COMMENT '需求导致延期',
  `develop_delays` decimal(3,1) NOT NULL COMMENT '研发导致延期',
  `smoking_by` tinyint(1) NOT NULL COMMENT '冒烟是否通过',
  `develop` varchar(50) NOT NULL COMMENT '研发人员',
  `item_reports_id` int NOT NULL COMMENT '迭代报告id',
  PRIMARY KEY (`id`),
  KEY `reports_story_item_reports_id_77159057_fk_reports_i` (`item_reports_id`),
  CONSTRAINT `reports_story_item_reports_id_77159057_fk_reports_i` FOREIGN KEY (`item_reports_id`) REFERENCES `reports_item_reports` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='故事表';


CREATE TABLE `reports_to_do` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `problem` varchar(255) NOT NULL COMMENT '问题描述',
  `solution` varchar(255) NOT NULL COMMENT '解决方案',
  `principal` varchar(10) NOT NULL COMMENT '负责人',
  `status` tinyint(1) NOT NULL COMMENT '解决状态',
  `remark` varchar(255) NOT NULL COMMENT '备注',
  `item_reports_id` int NOT NULL COMMENT '迭代报告id',
  PRIMARY KEY (`id`),
  KEY `reports_to_do_item_reports_id_40561ad6_fk_reports_i` (`item_reports_id`),
  CONSTRAINT `reports_to_do_item_reports_id_40561ad6_fk_reports_i` FOREIGN KEY (`item_reports_id`) REFERENCES `reports_item_reports` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8 COMMENT='待办表';

select * from reports_item_reports;
select * from reports_item_reports;
select * from reports_item_reports;