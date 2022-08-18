# -*- coding: utf-8 -*-
"""
@author   : Guo Hai Han
@software : PyCharm
@file     : goInception.py
@create   : 2022/8/3 15:18
"""
import pymysql
from dbms.models import DBServerConfig
from drf_admin.utils.crypt import BasePassword


class GoInceptionEngine(object):
    @staticmethod
    def get_connection():
        try:
            conn = pymysql.connect(host='0.0.0.0', user='', passwd='', db='', port=4000, charset="utf8mb4")
        except Exception as e:
            return {"error": "goInception连接数据库失败！失败原因：%s" % e}
        return conn

    @staticmethod
    def basic_info(db):
        """
        拼接数据库连接信息
        """
        try:
            queryset = DBServerConfig.objects.filter(id=db).values()[0]
            user = queryset["db_username"]
            password = BasePassword().get_password_display(queryset["db_password"])
            port = queryset["db_port"]
            host = queryset["db_ip"]
        except Exception as e:
            return {"error": "获取数据库连接的基本信息失败！失败原因：%s" % e}
        return host, user, password, port

    @staticmethod
    def execute(db, db_name, sql):
        """sql执行"""
        basic_info = GoInceptionEngine().basic_info(db)
        if isinstance(basic_info, dict):
            return basic_info
        host, user, password, port = basic_info
        sql_execute = f"""/*--user='{user}';--password='{password}';--host='{host}';--port={port};--execute=1;--ignore-warnings=1;*/
                                    inception_magic_start;
                                    use `{db_name}`;
                                    {sql.rstrip(';')};
                                    inception_magic_commit;"""
        result = GoInceptionEngine().query(sql_execute)
        return result

    @staticmethod
    def check(db, db_name, sql):
        """sql检查"""
        basic_info = GoInceptionEngine().basic_info(db)
        if isinstance(basic_info, dict):
            return basic_info
        host, user, password, port = basic_info
        sql_execute = f"""/*--user='{user}';--password='{password}';--host='{host}';--port={port};--check=1;--ignore-warnings=1;*/
                                    inception_magic_start;
                                    use `{db_name}`;
                                    {sql.rstrip(';')};
                                    inception_magic_commit;"""
        result = GoInceptionEngine().query(sql_execute)
        return result

    @staticmethod
    def query(sql):
        """负责执行goInception语句"""
        conn = GoInceptionEngine().get_connection()
        if isinstance(conn, dict):
            return conn
        cur = conn.cursor()
        try:
            cur.execute(sql)
        except Exception as e:
            return {"error": "goInception中sql执行失败！失败原因：%s" % e}
        data = {"title": [i[0] for i in cur.description], "infos": cur.fetchall()}
        cur.close()
        conn.close()
        return GoInceptionEngine().to_dict(data)

    @staticmethod
    def to_dict(data):
        """将返回sql执行结果以[{}, {}]形式返回"""
        result = {"errorCount": 0, "warningCount": 0, "rows": []}
        title = data["title"]
        infos = data["infos"]
        for info in infos:
            row = {}
            if info[2] == 1:
                result["warningCount"] += 1
            elif info[2] == 2:
                result["errorCount"] += 1
            for i in range(len(info)):
                row[title[i]] = info[i]
            result["rows"].append(row)
        return result
