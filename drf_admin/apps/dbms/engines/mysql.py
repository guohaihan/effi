# -*- coding: utf-8 -*-
"""
@author   : Guo Hai Han
@software : PyCharm
@file     : mysql.py
@create   : 2022/8/3 16:44
"""
from drf_admin.utils.crypt import BasePassword
from dbms.models import DBServerConfig
import pymysql


class MysqlEngine(object):
    def __init__(self, pk):
        self.pk = pk

    def basic_info(self):
        """
        拼接数据库连接信息
        """
        try:
            queryset = DBServerConfig.objects.filter(id=self.pk).values()[0]
            user = queryset["db_username"]
            passwd = BasePassword().get_password_display(queryset["db_password"])
            port = queryset["db_port"]
            db_name = None
            host = queryset["db_ip"]
            environment = DBServerConfig.objects.filter(id=self.pk)[0].get_db_env_display()
        except Exception as e:
            return {"error": "获取数据库连接的基本信息失败！失败原因：%s" % e}
        return {
            "host": host,
            "user": user,
            "passwd": passwd,
            "db_name": db_name,
            "port": port,
            "environment": environment
        }

    def get_connection(self):
        """获取连接conn"""
        basic_info = self.basic_info()
        if "error" in basic_info:
            return basic_info
        try:
            conn = pymysql.connect(
                host=basic_info["host"],
                user=basic_info["user"],
                passwd=basic_info["passwd"],
                port=basic_info["port"],
                database=basic_info["db_name"],
                charset='utf8',
                cursorclass=pymysql.cursors.DictCursor
            )
        except Exception as e:
            return {"error": "连接数据库失败！失败原因：%s" % e}
        return conn

    def execute_sql(self, sql):
        """
        执行sql命令
        :param sql: sql语句
        :return: 元祖
        """
        conn = self.get_connection()
        if isinstance(conn, dict):
            return conn
        cur = conn.cursor()  # 创建游标
        try:
            cur.execute(sql)
            res = cur.fetchall()  # 获取执行的返回结果
        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            return {"error": "sql执行失败！失败原因：%s；失败sql：%s" % (e, sql)}
        return res

    def get_all_db(self):
        """
        获取所有数据库名
        :return: list
        """
        # 排除自带的数据库
        exclude_list = ["sys", "information_schema", "mysql", "performance_schema"]
        sql = "show databases"  # 显示所有数据库
        res = self.execute_sql(sql)
        if isinstance(res, dict):
            return res
        else:
            res = [i for i in res if i["Database"] not in exclude_list]
            return res
