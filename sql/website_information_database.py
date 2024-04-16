import base64
import json
from datetime import datetime

import pymysql.connections


# import ConnectDB as connDB


def insert_website_information(conn: pymysql.connections.Connection, domain='www.google.com',
                               collection_task_start_time=None, collection_task_end_time=None,
                               ipv4_addr: list = None, ipv6_addr: list = None, ipv4_source_code=None,
                               ipv6_source_code=None,
                               ipv4_page_pic=None,
                               ipv6_page_pic=None, secondary_links: list = None, tertiary_links: list = None,
                               text_similarity=0.99, pic_similarity=0.99, text_structure_similarity=0.99):
    """
        插入网站信息到数据库中。

        :param conn: MySQL 连接对象。
        :param domain: 网站域名。
        :param collection_task_start_time: 采集任务开始时间，时间戳。
        :param collection_task_end_time: 采集任务结束时间，时间戳。
        :param ipv4_addr: IPv4 地址，传入list类型。
        :param ipv6_addr: IPv6 地址，传入list类型。
        :param ipv4_source_code: IPv4 源代码。
        :param ipv6_source_code: IPv6 源代码。
        :param ipv4_page_pic: IPv4 页面截图，格式为 base64 编码的字符串，这里会转会成blob类型存储到数据库中。
        :param ipv6_page_pic: IPv6 页面截图，格式为 base64 编码的字符串，这里会转会成blob类型存储到数据库中。
        :param secondary_links: 二级链接，格式为 list，这里会转换成JSON类型存储到数据库中。
        :param tertiary_links:  三级链接，格式为 list。
        :param text_similarity:    文本相似度，浮点数类型
        :param pic_similarity:      图片相似度，浮点数类型
        :param text_structure_similarity:   文本结构相似度，浮点数类型
        """
    sql = """INSERT INTO website_information(domain, collection_task_start_time, collection_task_end_time,
                                            ipv4_addr, ipv6_addr, ipv4_source_code, ipv6_source_code, ipv4_page_pic,
                                            ipv6_page_pic, secondary_links, tertiary_links, text_similarity, 
                                            pic_similarity, text_structure_similarity) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    # # 对于相应的参数进行格式转换
    # collection_task_start_time = datetime.strptime(collection_task_start_time, '%Y-%m-%d %H:%M:%S')
    # print(collection_task_start_time)
    # collection_task_end_time = datetime.strptime(collection_task_end_time, '%Y-%m-%d %H:%M:%S')

    # 在进入插入之前先进行查询，如果存在相应的结果，那么进行更新，如果不存在相应的结果，那么进行插入操作
    ipv4_page_pic = base64.b64decode(ipv4_page_pic)
    ipv6_page_pic = base64.b64decode(ipv6_page_pic)

    secondary_links = json.dumps({"secondary_links": secondary_links})
    tertiary_links = json.dumps({"tertiary_links": tertiary_links})

    ipv4_addr = json.dumps({"ipv4_addr": ipv4_addr})
    ipv6_addr = json.dumps({"ipv6_addr": ipv6_addr})

    result = query_website_information(conn, domain)
    if result is not None:
        update_website_information(conn, domain, collection_task_start_time, collection_task_end_time,
                                   ipv4_addr, ipv6_addr, ipv4_source_code, ipv6_source_code, ipv4_page_pic,
                                   ipv6_page_pic, secondary_links, tertiary_links, text_similarity,
                                   pic_similarity, text_structure_similarity)
    else:
        # 执行sql语句
        data_tuple = (domain, collection_task_start_time, collection_task_end_time, ipv4_addr, ipv6_addr, ipv4_source_code,
                      ipv6_source_code, ipv4_page_pic, ipv6_page_pic, secondary_links, tertiary_links, text_similarity,
                      pic_similarity, text_structure_similarity)
        cursor = conn.cursor()
        cursor.execute(sql, data_tuple)
        cursor.close()
        conn.commit()


def query_website_information(conn: pymysql.connections.Connection, domain='www.google.com'):
    """
        根据域名查询解析到的网站信息

        :param conn: MYSQL连接对象
        :param domain: 需要查询的域名
        :return: 返回对指定域名的查询结果
    """
    cursor = conn.cursor()
    sql = "SELECT * FROM website_information WHERE domain = %s"  # 没有直接传递参数，防止sql注入攻击
    cursor.execute(sql, domain)
    result = cursor.fetchall()
    # print(result)
    cursor.close()
    return result


def get_secondary_links(conn: pymysql.connections, domain='www.google.com'):
    """
        获取网站的二级链接

        :param conn:    MYSQL连接对象
        :param domain:  需要查询的域名
        :return:        返回一个list类型，包含所有的二级链接
    """
    cursor = conn.cursor()
    sql = "SELECT secondary_links FROM website_information WHERE domain = %s"
    cursor.execute(sql, domain)
    result = cursor.fetchall()
    result = json.loads(result[1][0])
    # print(result["secondary_links"])
    cursor.close()
    return result['secondary_links']


def get_tertiary_links(conn: pymysql.connections, domain='www.google.com'):
    """
        获取网站的三级链接

        :param conn:    MYSQL连接对象
        :param domain:  需要查询的域名
        :return:        返回一个list类型，包含所有的三级链接
    """
    cursor = conn.cursor()
    sql = "SELECT tertiary_links FROM website_information WHERE domain = %s"
    cursor.execute(sql, domain)
    result = cursor.fetchall()
    result = json.loads(result[1][0])
    # print(result["secondary_links"])
    cursor.close()
    return result['tertiary_links']


def get_ipv4_pic(conn: pymysql.connections, domain='www.google.com'):
    """
        获取ipv4下的网页截图

        :param conn:    MYSQL连接对象
        :param domain:  需要查询的域名
        :return:        返回的类型为二进制字节流
    """
    cursor = conn.cursor()
    sql = "SELECT ipv4_page_pic FROM website_information WHERE domain = %s"
    cursor.execute(sql, domain)
    result = cursor.fetchall()
    # 将blob格式返回为需要的类型
    cursor.close()
    return result


def get_ipv6_pic(conn: pymysql.connections, domain='www.google.com'):
    """
        获取ipv6下的网页截图

        :param conn:    MYSQL连接对象
        :param domain:  需要查询的域名
        :return:        返回的类型为二进制字节流
    """
    cursor = conn.cursor()
    sql = "SELECT ipv6_page_pic FROM website_information WHERE domain = %s"
    cursor.execute(sql, domain)
    result = cursor.fetchall()
    # 将blob格式返回为需要的类型
    cursor.close()
    return result


def update_website_information(conn: pymysql.connections.Connection, domain='www.google.com',
                               collection_task_start_time=None, collection_task_end_time=None,
                               ipv4_addr: list = None, ipv6_addr: list = None, ipv4_source_code=None,
                               ipv6_source_code=None,
                               ipv4_page_pic=None,
                               ipv6_page_pic=None, secondary_links: list = None, tertiary_links: list = None,
                               text_similarity=0.99, pic_similarity=0.99, text_structure_similarity=0.99):
    """
        执行更新操作，根据域名更新
    :param conn:
    :param domain:
    :param collection_task_start_time:
    :param collection_task_end_time:
    :param ipv4_addr:
    :param ipv6_addr:
    :param ipv4_source_code:
    :param ipv6_source_code:
    :param ipv4_page_pic:
    :param ipv6_page_pic:
    :param secondary_links:
    :param tertiary_links:
    :param text_similarity:
    :param pic_similarity:
    :param text_structure_similarity:
    :return:
    """
    sql = """UPDATE website_information SET collection_task_start_time = %s, collection_task_end_time = %s, 
            ipv4_addr = %s, ipv6_addr = %s,ipv4_source_code = %s, ipv6_source_code = %s, ipv4_page_pic = %s, 
            ipv6_page_pic =%s, secondary_links = %s, tertiary_links =%s, text_similarity =%s, pic_similarity = %s, 
            text_structure_similarity =%s WHERE domain = %s"""
    data_tuple = (collection_task_start_time, collection_task_end_time, ipv4_addr, ipv6_addr, ipv4_source_code,
                  ipv6_source_code, ipv4_page_pic, ipv6_page_pic, secondary_links, tertiary_links, text_similarity,
                  pic_similarity, text_structure_similarity, domain)
    cursor = conn.cursor()
    cursor.execute(sql, data_tuple)
    cursor.close()
    conn.commit()

# if __name__ == '__main__':
#     conn = connDB.get_mysql_conn()
#     # insert_website_information(conn)
#     # query_website_information(conn)
#     # get_secondary_links(conn)
#     conn.close()
