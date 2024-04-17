import datetime
import json

import pymysql

import sql.ConnectDB as connDB


def insert_support_degree(conn, domain='www.baidu.com', resolved=False, accessed=False, support_degree=95.09,
                          connectivity: str = None,
                          secondary_connectivity=None, tertiary_connectivity=None, resolve_delay=98.09,
                          tcp_establishment_resolution_delay=98.09, server_responds_first_packet_delay=98.09,
                          server_responds_first_page_delay=98.09, access_stability=None,
                          ipv6_authorization_system=False, start_time=datetime.datetime.now(), end_time=datetime.datetime.now(),
                          text_similarity=0.99, pic_similarity=0.99, text_structure_similarity=0.99):
    """
    插入新的ipv6支持度记录
    :param conn:    MYSQL连接对象
    :param domain:  网站域名
    :param resolved:    是否可以被解析
    :param accessed:    是否可以被访问
    :param support_degree:  ipv6支持度，默认为百分比,浮点类型
    :param connectivity:    ipv6连通性
    :param secondary_connectivity:  二级链接连通性，传入json类型，例如 {"connect":["www.baidu.com", "www.google.com"], "unconnect": []}
    :param tertiary_connectivity:   三级链接连通性, 传入json类型，同上
    :param resolve_delay:           域名解析时延指标，浮点类型
    :param tcp_establishment_resolution_delay:  TCP建立解析时延指标，浮点类型
    :param server_responds_first_packet_delay:  服务器响应首包时延指标，浮点类型
    :param server_responds_first_page_delay:    服务器响应首页时延指标，浮点类型
    :param access_stability:                    ipv6访问稳定性
    :param ipv6_authorization_system:           是否具备ipv6授权体系
    :param start_time:                          计算开始时间，使用时间戳
    :param end_time:                            计算完成时间，使用时间戳
    :param text_similarity:    文本相似度，浮点数类型
    :param pic_similarity:      图片相似度，浮点数类型
    :param text_structure_similarity:   文本结构相似度，浮点数类型
    :return:
    """
    data_tuple = (
        domain, resolved, accessed, support_degree, connectivity, secondary_connectivity, tertiary_connectivity,
        resolve_delay, tcp_establishment_resolution_delay,
        server_responds_first_packet_delay, server_responds_first_page_delay, access_stability,
        ipv6_authorization_system,
        start_time, end_time, text_similarity, pic_similarity, text_structure_similarity)
    result = query_ipv6_records(conn, domain)
    if result is not None:
        update_support_degree(conn, domain, resolved, accessed, support_degree, connectivity, secondary_connectivity,
                              tertiary_connectivity, resolve_delay, tcp_establishment_resolution_delay,
                              server_responds_first_packet_delay, server_responds_first_page_delay, access_stability,
                              ipv6_authorization_system, start_time, end_time, text_similarity, pic_similarity,
                              text_structure_similarity)
    else:
        sql = """INSERT INTO ipv6_support_degree (domain, resolved, accessed, support_degree, connectivity,
               secondary_connectivity, tertiary_connectivity, resolve_delay, tcp_establishment_resolution_delay, 
               server_responds_first_packet_delay, server_responds_first_page_delay, access_stability, ipv6_authorization_system, 
               start_time, end_time, text_similarity, pic_similarity, text_structure_similarity) 
               VALUES (%s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        cursor = conn.cursor()
        cursor.execute(sql, data_tuple)
        conn.commit()
        cursor.close()


def query_ipv6_records(conn: pymysql.connections.Connection, domain='www.google.com'):
    """
        根据域名查询解析到的网站信息

        :param conn: MYSQL连接对象
        :param domain: 需要查询的域名
        :return: 返回对指定域名的查询结果
    """
    cursor = conn.cursor()
    sql = "SELECT * FROM ipv6_support_degree WHERE domain = %s"  # 没有直接传递参数，防止sql注入攻击
    cursor.execute(sql, domain)
    result = cursor.fetchall()
    print(result[0])
    cursor.close()
    if len(result) == 0:
        return None
    return result[0]


def update_support_degree(conn, domain='www.google.com', resolved=False, accessed=False, support_degree=95.09,
                          connectivity: str = None,
                          secondary_connectivity=None, tertiary_connectivity=None, resolve_delay=98.09,
                          tcp_establishment_resolution_delay=98.09, server_responds_first_packet_delay=98.09,
                          server_responds_first_page_delay=98.09, access_stability=None,
                          ipv6_authorization_system=False, start_time=datetime.datetime.now(), end_time=datetime.datetime.now(),
                          text_similarity=0.99, pic_similarity=0.99, text_structure_similarity=0.99):
    """
    插入新的ipv6支持度记录
    :param conn:    MYSQL连接对象
    :param domain:  网站域名
    :param resolved:    是否可以被解析
    :param accessed:    是否可以被访问
    :param support_degree:  ipv6支持度，默认为百分比,浮点类型
    :param connectivity:    ipv6连通性
    :param secondary_connectivity:  二级链接连通性，传入json类型，例如 {"connect":["www.baidu.com", "www.google.com"], "unconnect": []}
    :param tertiary_connectivity:   三级链接连通性, 传入json类型，同上
    :param resolve_delay:           域名解析时延指标，浮点类型
    :param tcp_establishment_resolution_delay:  TCP建立解析时延指标，浮点类型
    :param server_responds_first_packet_delay:  服务器响应首包时延指标，浮点类型
    :param server_responds_first_page_delay:    服务器响应首页时延指标，浮点类型
    :param access_stability:                    ipv6访问稳定性
    :param ipv6_authorization_system:           是否具备ipv6授权体系
    :param start_time:                          计算开始时间，使用时间戳
    :param end_time:                            计算完成时间，使用时间戳
    :param text_similarity:    文本相似度，浮点数类型
    :param pic_similarity:      图片相似度，浮点数类型
    :param text_structure_similarity:   文本结构相似度，浮点数类型
    :return:
    """
    data_tuple = (
        resolved, accessed, support_degree, connectivity, secondary_connectivity, tertiary_connectivity,
        resolve_delay, tcp_establishment_resolution_delay,
        server_responds_first_packet_delay, server_responds_first_page_delay, access_stability,
        ipv6_authorization_system,
        start_time, end_time, text_similarity, pic_similarity, text_structure_similarity, domain)
    sql = """UPDATE ipv6_support_degree SET resolved = %s, accessed = %s, support_degree = %s, 
            connectivity = %s, secondary_connectivity = %s, tertiary_connectivity = %s, resolve_delay = %s, 
            tcp_establishment_resolution_delay = %s, server_responds_first_packet_delay = %s, 
            server_responds_first_page_delay = %s, access_stability = %s, ipv6_authorization_system = %s, 
            start_time = %s, end_time = %s, text_similarity = %s, pic_similarity = %s, text_structure_similarity = %s
            WHERE domain = %s"""

    cursor = conn.cursor()
    cursor.execute(sql, data_tuple)
    conn.commit()
    cursor.close()


# if __name__ == '__main__':
#     conn = connDB.get_mysql_conn()
#     # insert_support_degree(conn)
#     query_ipv6_records(conn)
#     conn.close()
