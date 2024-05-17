# -*- coding: utf-8 -*-
import os
import threading
import time
from datetime import datetime
from urllib.parse import urlparse
from information_collection import Information
from sql.ConnectDB import get_mysql_conn
from sql.support_degree_database import init_support_degree, insert_support_degree
from sql.website_information_database import insert_website_information, init_website_information
from support_degree_calc import IPv6SupportDegree
from test_domain_data.get_all_domains import get_num_domains
from flask import Flask, request, jsonify
from queue import Queue

app = Flask(__name__)
domain_list = Queue()
information_collection_list = Queue()
calc_support_list = Queue()
conn = get_mysql_conn()


def start_calc(domain):
    print(domain)
    if domain.startswith("http"):
        domain = urlparse(domain).hostname
    else:
        domain = domain
    start_time = datetime.now()
    ipv6SupportDegree = IPv6SupportDegree(domain)
    ipv6SupportDegree.calc_ipv6(conn)
    if ipv6SupportDegree.ipv6_resolution == 1:
        resolved = True
    else:
        resolved = False
    if ipv6SupportDegree.ipv6_http_server == 1 or ipv6SupportDegree.ipv6_https_server == 1:
        accessed = True
    else:
        accessed = False
    support_degree = ipv6SupportDegree.support_degree
    connectivity = ipv6SupportDegree.ipv6_connectivity
    secondary_connectivity = ipv6SupportDegree.ipv6_sub_connectivity
    tertiary_connectivity = ipv6SupportDegree.ipv6_third_connectivity
    resolve_delay = ipv6SupportDegree.dns_delay_ratio
    tcp_establishment_resolution_delay = ipv6SupportDegree.tcp_delay_ratio
    server_responds_first_packet_delay = ipv6SupportDegree.ack_delay_ratio
    server_responds_first_page_delay = ipv6SupportDegree.delay_ratio
    access_stability = ipv6SupportDegree.ipv6_stablity
    if ipv6SupportDegree.ipv6_authorization == 1:
        ipv6_authorization_system = True
    else:
        ipv6_authorization_system = False
    text_similarity = ipv6SupportDegree.text_similarity
    pic_similarity = ipv6SupportDegree.image_similarity
    text_structure_similarity = ipv6SupportDegree.structure_similarity

    end_time = datetime.now()
    insert_support_degree(conn, domain, resolved, accessed, support_degree, connectivity, secondary_connectivity,
                          tertiary_connectivity, resolve_delay, tcp_establishment_resolution_delay,
                          server_responds_first_packet_delay, server_responds_first_page_delay, access_stability,
                          ipv6_authorization_system, start_time, end_time, text_similarity, pic_similarity,
                          text_structure_similarity)


def start_collect(domain, path="./"):
    print(domain)
    if domain.startswith("http"):
        domain = urlparse(domain).hostname
    else:
        domain = domain
    information = Information(domain)
    collection_task_start_time = datetime.now()
    collection_task_start_time = collection_task_start_time.strftime('%Y-%m-%d %H:%M:%S')
    information.get_address(useIPv6=False)
    information.get_address(useIPv6=True)
    print(information.ipv4_address)
    print(information.ipv6_address)
    ipv4_pic = None
    ipv6_pic = None
    if information.supportIPv4:
        print("start ipv4")
        information.get_web_code(useIPv6=False)
        information.get_pic(path, useIPv6=False)
        # ipv4_pic = open(path + '{}.png'.format('ipv4.' + domain), 'rb').read()

    if information.supportIPv6:
        print("start ipv6")
        information.get_web_code(useIPv6=True)
        information.get_secondary_links()
        information.get_tertiary_links()
        information.get_pic(path, useIPv6=True)
        # ipv6_pic = open(path + '{}.png'.format('ipv6.' + domain), 'rb').read()

    collection_task_end_time = datetime.now()
    collection_task_end_time = collection_task_end_time.strftime('%Y-%m-%d %H:%M:%S')
    print("over")

    insert_website_information(conn, domain=domain,
                               collection_task_start_time=collection_task_start_time,
                               collection_task_end_time=collection_task_end_time,
                               ipv4_addr=information.ipv4_address, ipv6_addr=information.ipv6_address,
                               ipv4_source_code=information.ipv4_code, ipv6_source_code=information.ipv6_code,
                               ipv6_page_pic=ipv6_pic, ipv4_page_pic=ipv4_pic,
                               secondary_links=information.secondary_links, tertiary_links=information.tertiary_links)
    # if information.supportIPv4:
    #     os.remove(path + '{}.png'.format('ipv4.' + domain))
    # if information.supportIPv6:
    #     os.remove(path + '{}.png'.format('ipv6.' + domain))
    # conn.close()


def initialize_domain():
    while True:
        try:
            # 非阻塞地获取队列中的数据
            item = domain_list.get_nowait()
            print(item)
            print(f"Processing data: {item}")
            print("******************")
            conn = get_mysql_conn()
            # 将该域名插入到数据库中，并加入获取信息队列
            init_website_information(conn, domain=item)
            init_support_degree(conn, domain=item)
            # conn.close()
            print("*********************************************")
            information_collection_list.put(item)
            domain_list.task_done()
        except Exception as e:
            # print(f"No data in  initialize domain queue, waiting... {e}")
            time.sleep(3)


def information_collect():
    while True:
        try:
            # 非阻塞地获取队列中的数据
            item = information_collection_list.get_nowait()
            print(item)
            print(f"Processing data: {item}")
            # 获取网站信息
            start_collect(item, "./")
            calc_support_list.put(item)
            information_collection_list.task_done()
        except Exception as e:
            # print(f"No data in information collection queue, waiting... {e}")
            time.sleep(3)


def degree_calc():
    while True:
        try:
            # 非阻塞地获取队列中的数据
            item = calc_support_list.get_nowait()
            print(item)
            print(f"Processing data: {item}")
            # 获取网站信息
            start_calc(item)
            calc_support_list.task_done()
        except Exception as e:
            # print(f"No data in information collection queue, waiting... {e}")
            time.sleep(3)


@app.route('/add/domain', methods=['GET', 'POST'])
def add_url():
    if request.method == 'POST' or request.method == 'GET':
        try:
            if request.method == 'POST':
                data = request.json.get('domain')
            else:
                data = request.args.get('domain')
            if data is not None:
                if data.startswith("http"):
                    data = urlparse(data).hostname
                domain_list.put(data)  # 将数据放入队列
                return jsonify({'message': 'Number added to queue'}), 200
            else:
                return jsonify({'error': 'No number provided'}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'Invalid request method'}), 405


@app.route('/add/num', methods=['GET', 'POST'])
def add_domain_num():
    if request.method == 'POST' or request.method == 'GET':
        try:
            if request.method == 'POST':
                data = request.json.get('num')
            else:
                data = request.args.get('num')
            if data is not None:
                test_domains, test_urls = get_num_domains(int(data))
                for url in test_urls:
                    domain_list.put(url)
                return jsonify({'message': 'Number added to queue'}), 200
            else:
                return jsonify({'error': 'No number provided'}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'Invalid request method'}), 405


threading.Thread(target=initialize_domain, daemon=True).start()
threading.Thread(target=information_collect, daemon=True).start()
threading.Thread(target=degree_calc, daemon=True).start()
if __name__ == "__main__":
    app.run(host='0.0.0.0')
