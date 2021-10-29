CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `auth_group_permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=121 DEFAULT CHARSET=utf8;

CREATE TABLE `cmdb_accounts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(32) NOT NULL,
  `password` varchar(64) NOT NULL,
  `port` int unsigned NOT NULL,
  `server_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `cmdb_accounts_server_id_ec2329ef_fk_cmdb_servers_id` (`server_id`),
  CONSTRAINT `cmdb_accounts_server_id_ec2329ef_fk_cmdb_servers_id` FOREIGN KEY (`server_id`) REFERENCES `cmdb_servers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `cmdb_assets` (
  `id` int NOT NULL AUTO_INCREMENT,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `name` varchar(64) NOT NULL,
  `sn` varchar(128) NOT NULL,
  `asset_type` varchar(64) NOT NULL,
  `asset_status` smallint NOT NULL,
  `manage_ip` char(39) DEFAULT NULL,
  `expire_day` date DEFAULT NULL,
  `memo` longtext,
  `admin_id` int DEFAULT NULL,
  `cabinet_id` int DEFAULT NULL,
  `department_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `sn` (`sn`),
  KEY `cmdb_assets_admin_id_a98b12a9_fk_oauth_users_id` (`admin_id`),
  KEY `cmdb_assets_cabinet_id_be681fe1_fk_cmdb_cabinets_id` (`cabinet_id`),
  KEY `cmdb_assets_department_id_b6019634_fk_system_departments_id` (`department_id`),
  CONSTRAINT `cmdb_assets_admin_id_a98b12a9_fk_oauth_users_id` FOREIGN KEY (`admin_id`) REFERENCES `oauth_users` (`id`),
  CONSTRAINT `cmdb_assets_cabinet_id_be681fe1_fk_cmdb_cabinets_id` FOREIGN KEY (`cabinet_id`) REFERENCES `cmdb_cabinets` (`id`),
  CONSTRAINT `cmdb_assets_department_id_b6019634_fk_system_departments_id` FOREIGN KEY (`department_id`) REFERENCES `system_departments` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `cmdb_cabinets` (
  `id` int NOT NULL AUTO_INCREMENT,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `name` varchar(64) NOT NULL,
  `memo` varchar(128) DEFAULT NULL,
  `idc_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `cmdb_cabinets_idc_id_f10e1957_fk_cmdb_idc_id` (`idc_id`),
  CONSTRAINT `cmdb_cabinets_idc_id_f10e1957_fk_cmdb_idc_id` FOREIGN KEY (`idc_id`) REFERENCES `cmdb_idc` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `cmdb_idc` (
  `id` int NOT NULL AUTO_INCREMENT,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `name` varchar(64) NOT NULL,
  `memo` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `cmdb_networkdevices` (
  `id` int NOT NULL AUTO_INCREMENT,
  `device_type` smallint NOT NULL,
  `vlan_ip` char(39) DEFAULT NULL,
  `intranet_ip` char(39) DEFAULT NULL,
  `model` varchar(128) NOT NULL,
  `firmware` varchar(128) DEFAULT NULL,
  `port_num` smallint DEFAULT NULL,
  `device_detail` longtext,
  `asset_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `asset_id` (`asset_id`),
  CONSTRAINT `cmdb_networkdevices_asset_id_5b40c9c1_fk_cmdb_assets_id` FOREIGN KEY (`asset_id`) REFERENCES `cmdb_assets` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `cmdb_securitydevices` (
  `id` int NOT NULL AUTO_INCREMENT,
  `device_type` smallint NOT NULL,
  `model` varchar(128) NOT NULL,
  `asset_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `asset_id` (`asset_id`),
  CONSTRAINT `cmdb_securitydevices_asset_id_a12aed36_fk_cmdb_assets_id` FOREIGN KEY (`asset_id`) REFERENCES `cmdb_assets` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `cmdb_servers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `server_type` varchar(16) NOT NULL,
  `server_system_type` smallint NOT NULL,
  `model` varchar(128) DEFAULT NULL,
  `use` varchar(128) DEFAULT NULL,
  `asset_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `asset_id` (`asset_id`),
  CONSTRAINT `cmdb_servers_asset_id_61fcfab4_fk_cmdb_assets_id` FOREIGN KEY (`asset_id`) REFERENCES `cmdb_assets` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `cmdb_storagedevices` (
  `id` int NOT NULL AUTO_INCREMENT,
  `device_type` smallint NOT NULL,
  `model` varchar(128) NOT NULL,
  `asset_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `asset_id` (`asset_id`),
  CONSTRAINT `cmdb_storagedevices_asset_id_dd0245c6_fk_cmdb_assets_id` FOREIGN KEY (`asset_id`) REFERENCES `cmdb_assets` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `dbms_audits` (
  `id` int NOT NULL AUTO_INCREMENT,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `excute_db_name` longtext NOT NULL,
  `operate_sql` longtext NOT NULL,
  `user` varchar(20) NOT NULL,
  `auditor` varchar(20) DEFAULT NULL,
  `status` int NOT NULL,
  `reason` varchar(200) NOT NULL,
  `sprint` varchar(50) DEFAULT NULL,
  `db_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `dbms_audits_db_id_623f07aa_fk_dbms_config_info_id` (`db_id`),
  CONSTRAINT `dbms_audits_db_id_623f07aa_fk_dbms_config_info_id` FOREIGN KEY (`db_id`) REFERENCES `dbms_config_info` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=91 DEFAULT CHARSET=utf8;

CREATE TABLE `dbms_config_info` (
  `id` int NOT NULL AUTO_INCREMENT,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `db_env` int NOT NULL,
  `db_ip` varchar(50) NOT NULL,
  `db_type` int NOT NULL,
  `db_version` varchar(50) DEFAULT NULL,
  `db_name` varchar(50) NOT NULL,
  `db_username` varchar(32) NOT NULL,
  `db_password` varchar(128) NOT NULL,
  `db_port` int unsigned NOT NULL,
  `create_user` varchar(20) NOT NULL,
  `db_mark` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

CREATE TABLE `dbms_operate_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `env` varchar(20) NOT NULL,
  `db_name` varchar(50) NOT NULL,
  `operate_sql` longtext NOT NULL,
  `performer` varchar(20) NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `status` int NOT NULL,
  `error_info` longtext NOT NULL,
  `sprint` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=582 DEFAULT CHARSET=utf8;

CREATE TABLE `dbms_sqlscripts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `name` varchar(50) NOT NULL,
  `type` varchar(10) NOT NULL,
  `content` varchar(100) NOT NULL,
  `creator` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_oauth_users_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_oauth_users_id` FOREIGN KEY (`user_id`) REFERENCES `oauth_users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `django_apscheduler_djangojob` (
  `id` varchar(255) NOT NULL,
  `next_run_time` datetime(6) DEFAULT NULL,
  `job_state` longblob NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_apscheduler_djangojob_next_run_time_2f022619` (`next_run_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `django_apscheduler_djangojobexecution` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `status` varchar(50) NOT NULL,
  `run_time` datetime(6) NOT NULL,
  `duration` decimal(15,2) DEFAULT NULL,
  `finished` decimal(15,2) DEFAULT NULL,
  `exception` varchar(1000) DEFAULT NULL,
  `traceback` longtext,
  `job_id` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_apscheduler_djangojobexecution_run_time_16edd96b` (`run_time`),
  KEY `django_apscheduler_djangojobexecution_job_id_daf5090a_fk` (`job_id`),
  CONSTRAINT `django_apscheduler_djangojobexecution_job_id_daf5090a_fk` FOREIGN KEY (`job_id`) REFERENCES `django_apscheduler_djangojob` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8;

CREATE TABLE `django_migrations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=62 DEFAULT CHARSET=utf8;

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `easyaudit_crudevent` (
  `id` int NOT NULL AUTO_INCREMENT,
  `event_type` smallint NOT NULL,
  `object_id` varchar(255) NOT NULL,
  `object_repr` longtext,
  `object_json_repr` longtext,
  `datetime` datetime(6) NOT NULL,
  `content_type_id` int NOT NULL,
  `user_id` int DEFAULT NULL,
  `user_pk_as_string` varchar(255) DEFAULT NULL,
  `changed_fields` longtext,
  PRIMARY KEY (`id`),
  KEY `easyaudit_crudevent_content_type_id_618ed0c6_fk_django_co` (`content_type_id`),
  KEY `easyaudit_crudevent_user_id_09177b54_fk_oauth_users_id` (`user_id`),
  KEY `easyaudit_crudevent_object_id_content_type_id_48e7e97f_idx` (`object_id`,`content_type_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1551 DEFAULT CHARSET=utf8;

CREATE TABLE `easyaudit_loginevent` (
  `id` int NOT NULL AUTO_INCREMENT,
  `login_type` smallint NOT NULL,
  `username` varchar(255) DEFAULT NULL,
  `datetime` datetime(6) NOT NULL,
  `user_id` int DEFAULT NULL,
  `remote_ip` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `easyaudit_loginevent_user_id_f47fcbfb_fk_oauth_users_id` (`user_id`),
  KEY `easyaudit_loginevent_remote_ip_52fb5c3c` (`remote_ip`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `easyaudit_requestevent` (
  `id` int NOT NULL AUTO_INCREMENT,
  `url` varchar(254) NOT NULL,
  `method` varchar(20) NOT NULL,
  `query_string` longtext,
  `remote_ip` varchar(50) DEFAULT NULL,
  `datetime` datetime(6) NOT NULL,
  `user_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `easyaudit_requestevent_user_id_da412f45_fk_oauth_users_id` (`user_id`),
  KEY `easyaudit_requestevent_method_83a0c884` (`method`),
  KEY `easyaudit_requestevent_remote_ip_d43af9b2` (`remote_ip`),
  KEY `easyaudit_requestevent_url_37d1b8c4` (`url`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `monitor_errorlogs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `username` varchar(32) NOT NULL,
  `view` varchar(32) NOT NULL,
  `desc` longtext NOT NULL,
  `ip` char(39) NOT NULL,
  `detail` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=277 DEFAULT CHARSET=utf8;

CREATE TABLE `monitor_ipblacklist` (
  `id` int NOT NULL AUTO_INCREMENT,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `ip` char(39) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ip` (`ip`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `monitor_onlineusers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `ip` char(39) NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `monitor_onlineusers_user_id_248dbc65_fk_oauth_users_id` (`user_id`),
  CONSTRAINT `monitor_onlineusers_user_id_248dbc65_fk_oauth_users_id` FOREIGN KEY (`user_id`) REFERENCES `oauth_users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;

CREATE TABLE `oauth_users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `name` varchar(20) NOT NULL,
  `mobile` varchar(11) DEFAULT NULL,
  `image` varchar(100) NOT NULL,
  `department_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `mobile` (`mobile`),
  KEY `oauth_users_department_id_c38f9deb_fk_system_departments_id` (`department_id`),
  CONSTRAINT `oauth_users_department_id_c38f9deb_fk_system_departments_id` FOREIGN KEY (`department_id`) REFERENCES `system_departments` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

CREATE TABLE `oauth_users_groups` (
  `id` int NOT NULL AUTO_INCREMENT,
  `users_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `oauth_users_groups_users_id_group_id_a6d5dd23_uniq` (`users_id`,`group_id`),
  KEY `oauth_users_groups_group_id_234502cc_fk_auth_group_id` (`group_id`),
  CONSTRAINT `oauth_users_groups_group_id_234502cc_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `oauth_users_groups_users_id_84419b9f_fk_oauth_users_id` FOREIGN KEY (`users_id`) REFERENCES `oauth_users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `oauth_users_to_system_roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `users_id` int NOT NULL,
  `roles_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `oauth_users_to_system_roles_users_id_roles_id_f9870c0a_uniq` (`users_id`,`roles_id`),
  KEY `oauth_users_to_system_roles_roles_id_e553dfbf_fk_system_roles_id` (`roles_id`),
  CONSTRAINT `oauth_users_to_system_roles_roles_id_e553dfbf_fk_system_roles_id` FOREIGN KEY (`roles_id`) REFERENCES `system_roles` (`id`),
  CONSTRAINT `oauth_users_to_system_roles_users_id_b4775819_fk_oauth_users_id` FOREIGN KEY (`users_id`) REFERENCES `oauth_users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

CREATE TABLE `oauth_users_user_permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `users_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `oauth_users_user_permiss_users_id_permission_id_c70cd3b8_uniq` (`users_id`,`permission_id`),
  KEY `oauth_users_user_per_permission_id_74d25bb2_fk_auth_perm` (`permission_id`),
  CONSTRAINT `oauth_users_user_per_permission_id_74d25bb2_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `oauth_users_user_permissions_users_id_bb814e73_fk_oauth_users_id` FOREIGN KEY (`users_id`) REFERENCES `oauth_users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `system_departments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `name` varchar(32) NOT NULL,
  `pid_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `system_departments_pid_id_a20fc5d4_fk_system_departments_id` (`pid_id`),
  CONSTRAINT `system_departments_pid_id_a20fc5d4_fk_system_departments_id` FOREIGN KEY (`pid_id`) REFERENCES `system_departments` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `system_permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `name` varchar(30) NOT NULL,
  `sign` varchar(30) NOT NULL,
  `menu` tinyint(1) NOT NULL,
  `method` varchar(8) NOT NULL,
  `path` varchar(200) NOT NULL,
  `desc` varchar(30) NOT NULL,
  `pid_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sign` (`sign`),
  KEY `system_permissions_pid_id_d89bbee4_fk_system_permissions_id` (`pid_id`),
  CONSTRAINT `system_permissions_pid_id_d89bbee4_fk_system_permissions_id` FOREIGN KEY (`pid_id`) REFERENCES `system_permissions` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

CREATE TABLE `system_roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `name` varchar(32) NOT NULL,
  `desc` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;