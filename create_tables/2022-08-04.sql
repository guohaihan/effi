alter table dbms_audits change excute_db_name execute_db_name
    longtext NOT NULL COMMENT '要执行的数据库名';

alter table dbms_operate_logs modify error_info longtext;

CREATE TABLE `dbms_check_content` (
  `id` int NOT NULL AUTO_INCREMENT,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `sql_content` longtext NOT NULL,
  `status` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;