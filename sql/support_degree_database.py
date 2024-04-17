import datetime
import json
from PIL import Image
import io

import cursor as cursor
import pymysql
import sql.ConnectDB as connDB
from similarity.textSimilarity import calculate_sourcecode_similarity
from similarity.imageSimilarity import image_similarity

from support_degree_calc import try_ipv6_access
from support_degree_calc import  try_ipv6_resolution
from information_collection import  Information
from support_degree_calc import IPv6SupportDegree
from support_degree_calc import  get_Hostname
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
        print("完成更新!")
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
        print("完成插入!")


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

#保存文本相似度到数据库
def save_text_similarity(conn: pymysql.connections.Connection, domain='www.tsinghua.edu.cn'):
    cursor = conn.cursor()
    query_sql = "SELECT ipv4_source_code,ipv6_source_code FROM website_information WHERE domain = %s"
    cursor.execute(query_sql, domain)
    result = cursor.fetchall()
    for tuple_element in result:
        if tuple_element[0] and tuple_element[1]:
            text_similarity = calculate_sourcecode_similarity(tuple_element[0], tuple_element[1])
        else:
            text_similarity=0
        save_sql = """INSERT INTO ipv6_support_degree (domain,text_similarity) VALUES (%s, %s) ON DUPLICATE KEY UPDATE text_similarity = VALUES(text_similarity)"""
        cursor.execute(save_sql, (domain,text_similarity))
#保存图片相似度到数据库
def save_image_similarity(conn: pymysql.connections.Connection, domain='www.tsinghua.edu.cn'):
    cursor = conn.cursor()
    query_sql = "SELECT ipv4_page_pic,ipv6_page_pic FROM website_information WHERE domain = %s"
    cursor.execute(query_sql, domain)
    result = cursor.fetchall()
    for tuple_element in result:
        if tuple_element[0] and tuple_element[1]:
            #转化为PNG
            # 将 bytes 数据转换为 Image 对象
            ipv4Image = Image.open(io.BytesIO(tuple_element[0]))
            # 保存为 PNG 格式
            png_bytes = io.BytesIO()
            ipv4Image.save(png_bytes, format='PNG')
            ipv4Pic = png_bytes.getvalue()
            # 将 bytes 数据转换为 Image 对象
            ipv6Image = Image.open(io.BytesIO(tuple_element[1]))
            # 保存为 PNG 格式
            png_bytes = io.BytesIO()
            ipv6Image.save(png_bytes, format='PNG')
            ipv6Pic = png_bytes.getvalue()
            pic_similarity = image_similarity(ipv4Pic, ipv6Pic)
        else:
            pic_similarity=0
        save_sql = """INSERT INTO ipv6_support_degree (domain,pic_similarity) VALUES (%s, %s) ON DUPLICATE KEY UPDATE pic_similarity = VALUES(pic_similarity)"""
        cursor.execute(save_sql, (domain,pic_similarity))


#从数据库中查询文本相似度
def query_text_similarity(conn: pymysql.connections.Connection, domain='www.tsinghua.edu.cn'):
    print("域名：",domain)
    cursor = conn.cursor()
    query_sql = "SELECT text_similarity FROM ipv6_support_degree WHERE domain = %s"
    cursor.execute(query_sql, domain)
    result = cursor.fetchall()
    cursor.close()
    # print(result)
    return result
#从数据库中查询图片相似度
def query_image_similarity(conn: pymysql.connections.Connection, domain='www.tsinghua.edu.cn'):
    print("域名：",domain)
    cursor = conn.cursor()
    query_sql = "SELECT pic_similarity FROM ipv6_support_degree WHERE domain = %s"
    cursor.execute(query_sql, domain)
    result = cursor.fetchall()
    cursor.close()
    # print(result)
    return result

#对数据库中已有的所有domain的图片相似度进行保存和查询测试
def test_image_similaryt(conn):
    domain_list=get_all_domains_in_database(conn)
    for domain in domain_list:
        save_text_similarity(conn,domain)
        query_text_similarity(conn,domain)
        print("完成1条测试!")
#对数据库中已有的所有domain的文本相似度进行保存和查询测试
def test_text_similaryt(conn):
    domain_list=get_all_domains_in_database(conn)
    for domain in domain_list:
        save_image_similarity(conn,domain)
        query_image_similarity(conn,domain)
        print("完成1条测试!")

#获得数据库中所有域名domain
def get_all_domains_in_database(conn):
    cursor = conn.cursor()
    query_sql = "SELECT domain FROM website_information;"
    cursor.execute(query_sql)
    result_tuple = cursor.fetchall()
    domain_list=[]
    for result in result_tuple:
        domain=result[0]
        domain_list.append(domain)
    return domain_list

#保存是否可以被访问
def save_ipv6_accessed(conn: pymysql.connections.Connection, domain='www.tsinghua.edu.cn'):
    try:
        cursor = conn.cursor()
        accessed = try_ipv6_access(domain)
        # 检查domain是否存在
        query = "SELECT id FROM ipv6_support_degree WHERE domain = %s"
        cursor.execute(query, (domain,))
        result = cursor.fetchone()
        if result:
            # 如果存在，更新数据
            update_query = """
            UPDATE ipv6_support_degree SET accessed = %s WHERE domain = %s
            """
            cursor.execute(update_query, (accessed, domain))
        else:
            # 如果不存在，插入新数据
            insert_query = """
            INSERT INTO ipv6_support_degree (domain, accessed) VALUES (%s, %s)
            """
            cursor.execute(insert_query, (domain, accessed))
        # 提交事务
        conn.commit()
    except pymysql.MySQLError as e:
        conn.rollback()  # 发生错误时回滚事务
        print(f"An error occurred: {e}")
#保存是否可以被解析到数据库
def save_ipv6_resolved(conn: pymysql.connections.Connection, domain='www.tsinghua.edu.cn'):
    try:
        cursor = conn.cursor()
        resolved = try_ipv6_resolution(domain)
        # 检查domain是否存在
        query = "SELECT id FROM ipv6_support_degree WHERE domain = %s"
        cursor.execute(query, (domain,))
        result = cursor.fetchone()
        if result:
            # 如果存在，更新数据
            update_query = """
            UPDATE ipv6_support_degree SET resolved = %s WHERE domain = %s
            """
            cursor.execute(update_query, (resolved, domain))
        else:
            # 如果不存在，插入新数据
            insert_query = """
            INSERT INTO ipv6_support_degree (domain, resolved) VALUES (%s, %s)
            """
            cursor.execute(insert_query, (domain, resolved))
        # 提交事务
        conn.commit()
    except pymysql.MySQLError as e:
        conn.rollback()  # 发生错误时回滚事务
        print(f"An error occurred: {e}")
#保存二级链接连通性到数据库
def save_ipv6_secondary_connectivity(conn: pymysql.connections.Connection, domain='www.tsinghua.edu.cn'):
    try:
        cursor = conn.cursor()
        url = 'https://' + domain
        links = Information(url).get_secondary_links()
        print(links)
        result_dict = {"connect": [], "unconnect": []}
        for link in links:
            link_domain=get_Hostname(link)
            if try_ipv6_resolution(link_domain):
                result_dict["connect"].append(link_domain)
            else:
                result_dict["unconnect"].append(link_domain)
        # 将字典转换为 JSON 字符串
        secondary_connectivity_json = json.dumps(result_dict, ensure_ascii=False)
        # 检查 domain 是否存在
        query = "SELECT id FROM ipv6_support_degree WHERE domain = %s"
        cursor.execute(query, (domain,))
        db_result = cursor.fetchone()
        if db_result:
            # 如果存在，更新数据
            update_query = """
            UPDATE ipv6_support_degree SET secondary_connectivity = %s WHERE domain = %s
            """
            cursor.execute(update_query, (secondary_connectivity_json, domain))
        else:
            # 如果不存在，插入新数据
            insert_query = """
            INSERT INTO ipv6_support_degree (domain, secondary_connectivity) VALUES (%s, %s)
            """
            cursor.execute(insert_query, (domain, secondary_connectivity_json))
        # 提交事务
        conn.commit()
    except pymysql.MySQLError as e:
        conn.rollback()  # 发生错误时回滚事务
        print(f"An error occurred: {e}")
#保存三级链接连通性到数据库
def save_ipv6_tertiary_connectivity(conn: pymysql.connections.Connection, domain='www.tsinghua.edu.cn'):
    try:
        cursor = conn.cursor()
        url = 'https://' + domain
        links = Information(url).get_tertiary_links()
        print(links)
        result_dict = {"connect": [], "unconnect": []}
        for link in links:
            link_domain=get_Hostname(link)
            if try_ipv6_resolution(link_domain):
                result_dict["connect"].append(link_domain)
            else:
                result_dict["unconnect"].append(link_domain)
        # 将字典转换为 JSON 字符串
        tertiary_connectivity_json = json.dumps(result_dict, ensure_ascii=False)
        # 检查 domain 是否存在
        query = "SELECT id FROM ipv6_support_degree WHERE domain = %s"
        cursor.execute(query, (domain,))
        db_result = cursor.fetchone()
        if db_result:
            # 如果存在，更新数据
            update_query = """
            UPDATE ipv6_support_degree SET tertiary_connectivity = %s WHERE domain = %s
            """
            cursor.execute(update_query, (tertiary_connectivity_json, domain))
        else:
            # 如果不存在，插入新数据
            insert_query = """
            INSERT INTO ipv6_support_degree (domain, tertiary_connectivity) VALUES (%s, %s)
            """
            cursor.execute(insert_query, (domain, tertiary_connectivity_json))
        # 提交事务
        conn.commit()
    except pymysql.MySQLError as e:
        conn.rollback()  # 发生错误时回滚事务
        print(f"An error occurred: {e}")
#保存ipv6访问稳定性到数据库
def save_access_stability(conn: pymysql.connections.Connection, domain='www.tsinghua.edu.cn'):
    try:
        cursor = conn.cursor()
        url = 'https://'+domain
        access_stability= IPv6SupportDegree(url).test_ipv6_stablity()
        print(access_stability)
        print("##")
        # 检查domain是否存在
        query = "SELECT id FROM ipv6_support_degree WHERE domain = %s"
        cursor.execute(query, (domain,))
        result = cursor.fetchone()
        if result:
            # 如果存在，更新数据
            update_query = """
            UPDATE ipv6_support_degree SET access_stability = %s WHERE domain = %s
            """
            cursor.execute(update_query, (access_stability, domain))
        else:
            # 如果不存在，插入新数据
            insert_query = """
            INSERT INTO ipv6_support_degree (domain, access_stability) VALUES (%s, %s)
            """
            cursor.execute(insert_query, (domain, access_stability))
        # 提交事务
        conn.commit()
    except pymysql.MySQLError as e:
        conn.rollback()  # 发生错误时回滚事务
        print(f"An error occurred: {e}")
if __name__ == '__main__':
    conn = connDB.get_mysql_conn()
    # insert_support_degree(conn)
    # test_text_similaryt(conn)
    # save_text_similarity(conn)
    # query_text_similarity(conn)
    # # query_ipv6_records(conn)
    # conn = connDB.get_mysql_conn()
    save_ipv6_resolved(conn,"www.cupes.edu.cn")
    save_ipv6_accessed(conn, "www.cupes.edu.cn")
    save_ipv6_secondary_connectivity(conn,'www.tsinghua.edu.cn')
    save_ipv6_tertiary_connectivity(conn, 'www.tsinghua.edu.cn')
    # save_access_stability(conn, 'www.tsinghua.edu.cn')
    conn.close()