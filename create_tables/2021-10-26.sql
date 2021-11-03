CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='group';

CREATE TABLE `auth_group_permissions` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `group_id` int NOT NULL COMMENT 'group',
  `permission_id` int NOT NULL COMMENT 'permission',
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='group-permission relationship';

CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL COMMENT 'content type',
  `codename` varchar(100) NOT NULL COMMENT 'codename',
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=117 DEFAULT CHARSET=utf8 COMMENT='permission';

CREATE TABLE `cmdb_accounts` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `username` varchar(32) NOT NULL COMMENT '登录账户',
  `password` varchar(64) NOT NULL COMMENT '登录密码',
  `port` int unsigned NOT NULL COMMENT '登录端口号',
  `server_id` int NOT NULL COMMENT '服务器',
  PRIMARY KEY (`id`),
  KEY `cmdb_accounts_server_id_ec2329ef_fk_cmdb_servers_id` (`server_id`),
  CONSTRAINT `cmdb_accounts_server_id_ec2329ef_fk_cmdb_servers_id` FOREIGN KEY (`server_id`) REFERENCES `cmdb_servers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='服务器登录账户';

CREATE TABLE `cmdb_assets` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `create_time` datetime(6) NOT NULL COMMENT '创建时间',
  `update_time` datetime(6) NOT NULL COMMENT '更新时间',
  `name` varchar(64) NOT NULL COMMENT '资产名称',
  `sn` varchar(128) NOT NULL COMMENT '资产序列号',
  `asset_type` varchar(64) NOT NULL COMMENT '资产类型',
  `asset_status` smallint NOT NULL COMMENT '设备状态',
  `manage_ip` char(39) DEFAULT NULL COMMENT '管理IP',
  `expire_day` date DEFAULT NULL COMMENT '过保日期',
  `memo` longtext COMMENT '备注',
  `admin_id` int DEFAULT NULL COMMENT '资产管理员',
  `cabinet_id` int DEFAULT NULL COMMENT '所在机柜',
  `department_id` int DEFAULT NULL COMMENT '所属部门',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `sn` (`sn`),
  KEY `cmdb_assets_admin_id_a98b12a9_fk_oauth_users_id` (`admin_id`),
  KEY `cmdb_assets_cabinet_id_be681fe1_fk_cmdb_cabinets_id` (`cabinet_id`),
  KEY `cmdb_assets_department_id_b6019634_fk_system_departments_id` (`department_id`),
  CONSTRAINT `cmdb_assets_admin_id_a98b12a9_fk_oauth_users_id` FOREIGN KEY (`admin_id`) REFERENCES `oauth_users` (`id`),
  CONSTRAINT `cmdb_assets_cabinet_id_be681fe1_fk_cmdb_cabinets_id` FOREIGN KEY (`cabinet_id`) REFERENCES `cmdb_cabinets` (`id`),
  CONSTRAINT `cmdb_assets_department_id_b6019634_fk_system_departments_id` FOREIGN KEY (`department_id`) REFERENCES `system_departments` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='资产总表';

CREATE TABLE `cmdb_cabinets` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `create_time` datetime(6) NOT NULL COMMENT '创建时间',
  `update_time` datetime(6) NOT NULL COMMENT '更新时间',
  `name` varchar(64) NOT NULL COMMENT '机柜名称',
  `memo` varchar(128) DEFAULT NULL COMMENT '备注',
  `idc_id` int DEFAULT NULL COMMENT '所在机房',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `cmdb_cabinets_idc_id_f10e1957_fk_cmdb_idc_id` (`idc_id`),
  CONSTRAINT `cmdb_cabinets_idc_id_f10e1957_fk_cmdb_idc_id` FOREIGN KEY (`idc_id`) REFERENCES `cmdb_idc` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='机柜';

CREATE TABLE `cmdb_idc` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `create_time` datetime(6) NOT NULL COMMENT '创建时间',
  `update_time` datetime(6) NOT NULL COMMENT '更新时间',
  `name` varchar(64) NOT NULL COMMENT '机房名称',
  `memo` varchar(128) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='机房';

CREATE TABLE `cmdb_networkdevices` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `device_type` smallint NOT NULL COMMENT '网络设备类型',
  `vlan_ip` char(39) DEFAULT NULL COMMENT 'VLanIP',
  `intranet_ip` char(39) DEFAULT NULL COMMENT '内网IP',
  `model` varchar(128) NOT NULL COMMENT '网络设备型号',
  `firmware` varchar(128) DEFAULT NULL COMMENT '设备固件版本',
  `port_num` smallint DEFAULT NULL COMMENT '端口个数',
  `device_detail` longtext COMMENT '详细配置',
  `asset_id` int NOT NULL COMMENT 'asset',
  PRIMARY KEY (`id`),
  UNIQUE KEY `asset_id` (`asset_id`),
  CONSTRAINT `cmdb_networkdevices_asset_id_5b40c9c1_fk_cmdb_assets_id` FOREIGN KEY (`asset_id`) REFERENCES `cmdb_assets` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='网络设备';

CREATE TABLE `cmdb_securitydevices` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `device_type` smallint NOT NULL COMMENT '安全设备类型',
  `model` varchar(128) NOT NULL COMMENT '安全设备型号',
  `asset_id` int NOT NULL COMMENT 'asset',
  PRIMARY KEY (`id`),
  UNIQUE KEY `asset_id` (`asset_id`),
  CONSTRAINT `cmdb_securitydevices_asset_id_a12aed36_fk_cmdb_assets_id` FOREIGN KEY (`asset_id`) REFERENCES `cmdb_assets` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='安全设备';

CREATE TABLE `cmdb_servers` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `server_type` varchar(16) NOT NULL COMMENT '服务器类型',
  `server_system_type` smallint NOT NULL COMMENT '服务器系统类型',
  `model` varchar(128) DEFAULT NULL COMMENT '服务器型号',
  `use` varchar(128) DEFAULT NULL COMMENT '用途',
  `asset_id` int NOT NULL COMMENT 'asset',
  PRIMARY KEY (`id`),
  UNIQUE KEY `asset_id` (`asset_id`),
  CONSTRAINT `cmdb_servers_asset_id_61fcfab4_fk_cmdb_assets_id` FOREIGN KEY (`asset_id`) REFERENCES `cmdb_assets` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='服务器';

CREATE TABLE `cmdb_storagedevices` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `device_type` smallint NOT NULL COMMENT '存储设备类型',
  `model` varchar(128) NOT NULL COMMENT '存储设备型号',
  `asset_id` int NOT NULL COMMENT 'asset',
  PRIMARY KEY (`id`),
  UNIQUE KEY `asset_id` (`asset_id`),
  CONSTRAINT `cmdb_storagedevices_asset_id_dd0245c6_fk_cmdb_assets_id` FOREIGN KEY (`asset_id`) REFERENCES `cmdb_assets` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='存储设备';

CREATE TABLE `dbms_audits` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `create_time` datetime(6) NOT NULL COMMENT '创建时间',
  `update_time` datetime(6) NOT NULL COMMENT '更新时间',
  `excute_db_name` longtext NOT NULL COMMENT '要执行的数据库名',
  `operate_sql` longtext NOT NULL COMMENT '要执行的sql',
  `user` varchar(20) NOT NULL COMMENT '申请人',
  `auditor` varchar(20) DEFAULT NULL COMMENT '审核人',
  `status` int NOT NULL COMMENT '审核状态',
  `reason` varchar(200) NOT NULL COMMENT '驳回理由',
  `sprint` varchar(50) DEFAULT NULL COMMENT '分支',
  `db_id` int NOT NULL COMMENT '关联数据库id',
  PRIMARY KEY (`id`),
  KEY `dbms_audits_db_id_623f07aa_fk_dbms_config_info_id` (`db_id`),
  CONSTRAINT `dbms_audits_db_id_623f07aa_fk_dbms_config_info_id` FOREIGN KEY (`db_id`) REFERENCES `dbms_config_info` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='sql审核表';

CREATE TABLE `dbms_config_info` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `create_time` datetime(6) NOT NULL COMMENT '创建时间',
  `update_time` datetime(6) NOT NULL COMMENT '更新时间',
  `db_env` int NOT NULL COMMENT '环境类型',
  `db_ip` varchar(50) NOT NULL COMMENT 'ip地址',
  `db_type` int NOT NULL COMMENT '数据库类型',
  `db_version` varchar(50) DEFAULT NULL COMMENT '数据库版本',
  `db_mark` varchar(200) DEFAULT NULL COMMENT '备注',
  `db_name` varchar(50) NOT NULL COMMENT '数据库名称',
  `db_username` varchar(32) NOT NULL COMMENT '登录账户',
  `db_password` varchar(128) NOT NULL COMMENT '登录密码',
  `db_port` int unsigned NOT NULL COMMENT '登录端口号',
  `create_user` varchar(20) NOT NULL COMMENT '创建者',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='数据库连接信息';

CREATE TABLE `dbms_operate_logs` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `env` varchar(20) NOT NULL COMMENT '执行环境',
  `db_name` varchar(50) NOT NULL COMMENT '数据库名',
  `operate_sql` longtext NOT NULL COMMENT '执行语句',
  `performer` varchar(20) NOT NULL COMMENT '执行者',
  `create_time` datetime(6) NOT NULL COMMENT '创建时间',
  `status` int NOT NULL COMMENT '执行状态',
  `error_info` longtext NOT NULL COMMENT 'message',
  `sprint` varchar(50) DEFAULT NULL COMMENT '分支',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='sql执行记录';

CREATE TABLE `dbms_sqlscripts` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `create_time` datetime(6) NOT NULL COMMENT '创建时间',
  `update_time` datetime(6) NOT NULL COMMENT '更新时间',
  `name` varchar(50) NOT NULL COMMENT '名称',
  `type` varchar(10) NOT NULL COMMENT '类型',
  `content` varchar(100) NOT NULL COMMENT '文件内容',
  `creator` varchar(20) NOT NULL COMMENT '创建者',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='果之sql脚本';

CREATE TABLE `easyaudit_crudevent` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `event_type` smallint NOT NULL COMMENT 'event type',
  `object_id` varchar(255) NOT NULL,
  `object_repr` longtext,
  `object_json_repr` longtext COMMENT 'object json repr',
  `datetime` datetime(6) NOT NULL COMMENT 'datetime',
  `content_type_id` int NOT NULL COMMENT 'content type',
  `user_id` int DEFAULT NULL COMMENT 'user',
  `user_pk_as_string` varchar(255) DEFAULT NULL COMMENT 'user pk as string',
  `changed_fields` longtext COMMENT 'changed fields',
  PRIMARY KEY (`id`),
  KEY `easyaudit_crudevent_content_type_id_618ed0c6_fk_django_co` (`content_type_id`),
  KEY `easyaudit_crudevent_user_id_09177b54_fk_oauth_users_id` (`user_id`),
  KEY `easyaudit_crudevent_object_id_content_type_id_48e7e97f_idx` (`object_id`,`content_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='CRUD event';

CREATE TABLE `easyaudit_loginevent` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `login_type` smallint NOT NULL COMMENT 'login type',
  `username` varchar(255) DEFAULT NULL COMMENT 'username',
  `datetime` datetime(6) NOT NULL COMMENT 'datetime',
  `user_id` int DEFAULT NULL COMMENT 'user',
  `remote_ip` varchar(50) DEFAULT NULL COMMENT 'remote ip',
  PRIMARY KEY (`id`),
  KEY `easyaudit_loginevent_user_id_f47fcbfb_fk_oauth_users_id` (`user_id`),
  KEY `easyaudit_loginevent_remote_ip_52fb5c3c` (`remote_ip`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='login event';

CREATE TABLE `easyaudit_requestevent` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `url` varchar(254) NOT NULL,
  `method` varchar(20) NOT NULL COMMENT 'method',
  `query_string` longtext,
  `remote_ip` varchar(50) DEFAULT NULL COMMENT 'remote ip',
  `datetime` datetime(6) NOT NULL COMMENT 'datetime',
  `user_id` int DEFAULT NULL COMMENT 'user',
  PRIMARY KEY (`id`),
  KEY `easyaudit_requestevent_user_id_da412f45_fk_oauth_users_id` (`user_id`),
  KEY `easyaudit_requestevent_method_83a0c884` (`method`),
  KEY `easyaudit_requestevent_remote_ip_d43af9b2` (`remote_ip`),
  KEY `easyaudit_requestevent_url_37d1b8c4` (`url`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='request event';

CREATE TABLE `monitor_errorlogs` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `create_time` datetime(6) NOT NULL COMMENT '创建时间',
  `update_time` datetime(6) NOT NULL COMMENT '更新时间',
  `username` varchar(32) NOT NULL COMMENT '用户',
  `view` varchar(32) NOT NULL COMMENT '视图',
  `desc` longtext NOT NULL COMMENT '描述',
  `ip` char(39) NOT NULL COMMENT 'IP',
  `detail` longtext NOT NULL COMMENT '详情',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='错误日志';

CREATE TABLE `monitor_ipblacklist` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `create_time` datetime(6) NOT NULL COMMENT '创建时间',
  `update_time` datetime(6) NOT NULL COMMENT '更新时间',
  `ip` char(39) NOT NULL COMMENT 'IP',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ip` (`ip`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='IP黑名单';

CREATE TABLE `monitor_onlineusers` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `create_time` datetime(6) NOT NULL COMMENT '创建时间',
  `update_time` datetime(6) NOT NULL COMMENT '更新时间',
  `ip` char(39) NOT NULL COMMENT 'IP',
  `user_id` int NOT NULL COMMENT '用户',
  PRIMARY KEY (`id`),
  KEY `monitor_onlineusers_user_id_248dbc65_fk_oauth_users_id` (`user_id`),
  CONSTRAINT `monitor_onlineusers_user_id_248dbc65_fk_oauth_users_id` FOREIGN KEY (`user_id`) REFERENCES `oauth_users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='在线用户';

CREATE TABLE `oauth_users` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `password` varchar(128) NOT NULL COMMENT 'password',
  `last_login` datetime(6) DEFAULT NULL COMMENT 'last login',
  `is_superuser` tinyint(1) NOT NULL COMMENT 'superuser status',
  `username` varchar(150) NOT NULL COMMENT 'username',
  `first_name` varchar(30) NOT NULL COMMENT 'first name',
  `last_name` varchar(150) NOT NULL COMMENT 'last name',
  `email` varchar(254) NOT NULL COMMENT 'email address',
  `is_staff` tinyint(1) NOT NULL COMMENT 'staff status',
  `is_active` tinyint(1) NOT NULL COMMENT 'active',
  `date_joined` datetime(6) NOT NULL COMMENT 'date joined',
  `name` varchar(20) NOT NULL COMMENT '真实姓名',
  `mobile` varchar(11) DEFAULT NULL COMMENT '手机号码',
  `image` varchar(100) NOT NULL COMMENT '头像',
  `department_id` int DEFAULT NULL COMMENT '部门',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `mobile` (`mobile`),
  KEY `oauth_users_department_id_c38f9deb_fk_system_departments_id` (`department_id`),
  CONSTRAINT `oauth_users_department_id_c38f9deb_fk_system_departments_id` FOREIGN KEY (`department_id`) REFERENCES `system_departments` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='用户';

CREATE TABLE `oauth_users_groups` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `users_id` int NOT NULL COMMENT 'users',
  `group_id` int NOT NULL COMMENT 'group',
  PRIMARY KEY (`id`),
  UNIQUE KEY `oauth_users_groups_users_id_group_id_a6d5dd23_uniq` (`users_id`,`group_id`),
  KEY `oauth_users_groups_group_id_234502cc_fk_auth_group_id` (`group_id`),
  CONSTRAINT `oauth_users_groups_group_id_234502cc_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `oauth_users_groups_users_id_84419b9f_fk_oauth_users_id` FOREIGN KEY (`users_id`) REFERENCES `oauth_users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='users-group relationship';

CREATE TABLE `oauth_users_to_system_roles` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `users_id` int NOT NULL COMMENT 'users',
  `roles_id` int NOT NULL COMMENT 'roles',
  PRIMARY KEY (`id`),
  UNIQUE KEY `oauth_users_to_system_roles_users_id_roles_id_f9870c0a_uniq` (`users_id`,`roles_id`),
  KEY `oauth_users_to_system_roles_roles_id_e553dfbf_fk_system_roles_id` (`roles_id`),
  CONSTRAINT `oauth_users_to_system_roles_roles_id_e553dfbf_fk_system_roles_id` FOREIGN KEY (`roles_id`) REFERENCES `system_roles` (`id`),
  CONSTRAINT `oauth_users_to_system_roles_users_id_b4775819_fk_oauth_users_id` FOREIGN KEY (`users_id`) REFERENCES `oauth_users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='users-roles relationship';

CREATE TABLE `oauth_users_user_permissions` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `users_id` int NOT NULL COMMENT 'users',
  `permission_id` int NOT NULL COMMENT 'permission',
  PRIMARY KEY (`id`),
  UNIQUE KEY `oauth_users_user_permiss_users_id_permission_id_c70cd3b8_uniq` (`users_id`,`permission_id`),
  KEY `oauth_users_user_per_permission_id_74d25bb2_fk_auth_perm` (`permission_id`),
  CONSTRAINT `oauth_users_user_per_permission_id_74d25bb2_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `oauth_users_user_permissions_users_id_bb814e73_fk_oauth_users_id` FOREIGN KEY (`users_id`) REFERENCES `oauth_users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='users-permission relationship';

CREATE TABLE `system_departments` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `create_time` datetime(6) NOT NULL COMMENT '创建时间',
  `update_time` datetime(6) NOT NULL COMMENT '更新时间',
  `name` varchar(32) NOT NULL COMMENT '部门',
  `pid_id` int DEFAULT NULL COMMENT '父部门',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `system_departments_pid_id_a20fc5d4_fk_system_departments_id` (`pid_id`),
  CONSTRAINT `system_departments_pid_id_a20fc5d4_fk_system_departments_id` FOREIGN KEY (`pid_id`) REFERENCES `system_departments` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='部门';

CREATE TABLE `system_permissions` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `create_time` datetime(6) NOT NULL COMMENT '创建时间',
  `update_time` datetime(6) NOT NULL COMMENT '更新时间',
  `name` varchar(30) NOT NULL COMMENT '权限名',
  `sign` varchar(30) NOT NULL COMMENT '权限标识',
  `menu` tinyint(1) NOT NULL COMMENT '是否为菜单',
  `method` varchar(8) NOT NULL COMMENT '方法',
  `path` varchar(200) NOT NULL COMMENT '请求路径正则',
  `desc` varchar(30) NOT NULL COMMENT '权限描述',
  `pid_id` int DEFAULT NULL COMMENT '父权限',
  PRIMARY KEY (`id`),
  UNIQUE KEY `sign` (`sign`),
  KEY `system_permissions_pid_id_d89bbee4_fk_system_permissions_id` (`pid_id`),
  CONSTRAINT `system_permissions_pid_id_d89bbee4_fk_system_permissions_id` FOREIGN KEY (`pid_id`) REFERENCES `system_permissions` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='权限';

CREATE TABLE `system_roles` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `create_time` datetime(6) NOT NULL COMMENT '创建时间',
  `update_time` datetime(6) NOT NULL COMMENT '更新时间',
  `name` varchar(32) NOT NULL COMMENT '角色',
  `desc` varchar(50) NOT NULL COMMENT '描述',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='角色';

CREATE TABLE `system_roles_to_system_permissions` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `roles_id` int NOT NULL COMMENT 'roles',
  `permissions_id` int NOT NULL COMMENT 'permissions',
  PRIMARY KEY (`id`),
  UNIQUE KEY `system_roles_to_system_p_roles_id_permissions_id_cc02d6be_uniq` (`roles_id`,`permissions_id`),
  KEY `system_roles_to_syst_permissions_id_6b98c1d9_fk_system_pe` (`permissions_id`),
  CONSTRAINT `system_roles_to_syst_permissions_id_6b98c1d9_fk_system_pe` FOREIGN KEY (`permissions_id`) REFERENCES `system_permissions` (`id`),
  CONSTRAINT `system_roles_to_syst_roles_id_ff9d45cd_fk_system_ro` FOREIGN KEY (`roles_id`) REFERENCES `system_roles` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='roles-permissions relationship';