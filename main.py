# -*- coding: utf-8 -*-
import concurrent.futures
from datetime import datetime
from urllib.parse import urlparse

from information_collection import Information
from sql.ConnectDB import get_mysql_conn
from sql.website_information_database2 import insert_website_information
from test_domain_data.get_all_domains import get_num_domains

def information_collect(ip_address, path="./"):
    print(ip_address)
    information = Information(ip_address)
    collection_task_start_time = datetime.now()
    collection_task_start_time = collection_task_start_time.strftime('%Y-%m-%d %H:%M:%S')

    # information.get_pic(path, True)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            "get_ipv4_address": executor.submit(information.get_address(useIPv6=False)),
            "get_ipv6_address": executor.submit(information.get_address(useIPv6=True)),
        }
        concurrent.futures.wait(
            [futures["get_ipv4_address"], futures["get_ipv6_address"]]
        )
    print("aaa")
    print(information.ipv4_address)
    print(information.ipv6_address)
    if information.supportIPv4:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                "get_ipv4_code": executor.submit(information.get_web_code(useIPv6=False)),
                "get_ipv4_pic": executor.submit(information.get_pic(path, useIPv6=False)),
            }
            concurrent.futures.wait(
                [futures["get_ipv4_code"], futures["get_ipv4_pic"]]
            )
    print("bbb")
    if information.supportIPv6:
        information.get_pic(path, useIPv6=True)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                "get_ipv6_code": executor.submit(information.get_web_code(useIPv6=True)),
                # "get_ipv6_pic": executor.submit(information.get_pic(path, useIPv6=True)),
                "get_secondary_links": executor.submit(information.get_secondary_links()),
            }
            concurrent.futures.wait(
                # [futures["get_ipv6_code"], futures["get_ipv6_pic"], futures["get_secondary_links"]]
                [futures["get_ipv6_code"], futures["get_secondary_links"]]
            )
    print("ccc")
    # information.get_tertiary_links()
    print(information.secondary_links)
    collection_task_end_time = datetime.now()
    collection_task_end_time = collection_task_end_time.strftime('%Y-%m-%d %H:%M:%S')

    if ip_address.startswith("http"):
        domain = urlparse(ip_address).hostname
    else:
        domain = ip_address

    ipv4_pic = ""
    ipv6_pic = ""
    try:
        ipv4_file = open(path + '{}.png'.format('ipv4.' + domain), 'rb')
        ipv4_pic = ipv4_file.read()
    except FileNotFoundError as e:
        print(e)
    try:
        ipv6_file = open(path + '{}.png'.format('ipv6.' + domain), 'rb')
        ipv6_pic = ipv6_file.read()
    except FileNotFoundError as e:
        print(e)

    insert_website_information(get_mysql_conn(), domain=domain,
                               collection_task_start_time=collection_task_start_time,
                               collection_task_end_time=collection_task_end_time,
                               ipv4_addr=information.ipv4_address, ipv6_addr=information.ipv6_address,
                               ipv4_source_code=information.ipv4_code, ipv6_source_code=information.ipv6_code,
                               ipv6_page_pic=ipv6_pic, ipv4_page_pic=ipv4_pic,
                               secondary_links=information.secondary_links, tertiary_links=information.tertiary_links)

#插入多条数据
def insert_moredomain_information(num=4):
    test_domains,test_urls=get_num_domains(num)
    for url in test_urls:
        information_collect(url)


if __name__ == "__main__":
    insert_moredomain_information(num=4)#选择num个网址插入数据到数据库

