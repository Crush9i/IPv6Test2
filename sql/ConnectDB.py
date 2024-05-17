# -*- coding: UTF-8 -*-
import pymysql

# 1. 这里是数据库超参数
host = 'localhost'  # mysql地址,填写域名或者ip地址
database_user = "root"  # mysql 用户名
database_passwd = "root"  # mysql 密码
database = "ipv6test"  # 需要连接的数据库


def get_mysql_conn():
    # 2. 连接数据库操作
    try:
        conn = pymysql.connect(database=database,
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


if __name__ == "__main__":
    conn = get_mysql_conn()
    conn.close()
