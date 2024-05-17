# -*- coding: UTF-8 -*-
import re

import pymysql

# 1. 这里是数据库超参数
host = 'localhost'  # mysql地址,填写域名或者ip地址
database_user = "root"  # mysql 用户名
database_passwd = "root"  # mysql 密码
database = "ipv6test"  # 需要连接的数据库


def get_mysql_conn():
    # 2. 连接数据库操作
    try:
        conn = pymysql.connect(#这里我把数据库删除了
                               host=host,
                               user=database_user,
                               password=database_passwd,
                               charset='utf8mb4')
        print(f'Connected to MySQL database {database}')
    except pymysql.MySQLError as e:
        print("Error", e)
    finally:
        if conn is not None:
            return conn
        else:
            return None



def execute_sql_file(filename,db_name):#执行sql文件（filename）并创建和使用数据库db_name进行存储
    conn = get_mysql_conn()
    cursor = conn.cursor()
    try:#创建数据库db_name
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name};")
        print(f"数据库 '{db_name}' 成功创建!")
    except Exception as err:
        print(f"数据库创建失败: {err}")
    try:#使用数据库db_name
        cursor.execute(f"use {db_name};")
        print(f"使用数据库{db_name}:")
    except Exception as e:
        print(f"使用数据库{db_name}失败!")
    i = 0
    results= ""
    try:
        with open(filename, mode="r+", encoding="utf-8") as r:
            for sql in r.readlines():
                # 获取不是“-- ”的数据
                if not sql.startswith("-- "):
                    results = results + sql
            results=re.sub(r'/\*.*?\*/','',results,flags=re.DOTALL)
            for sql_statement in results.split(";"):
                if sql_statement.strip():
                    print(i, " ", sql_statement.strip())
                    cursor.execute(sql_statement.strip())
                    conn.commit()
                    i+=1
    except Exception as e:
        print("SQL文件执行出错:", e)
    finally:
        cursor.close()
        # 关闭数据库连接
        conn.close()
        print("SQL文件执行成功！")

if __name__ == "__main__":
    # conn = get_mysql_conn()
    # conn.close()
    execute_sql_file('./ipv6test_new.sql',database)
