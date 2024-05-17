# -*- coding: utf-8 -*-
import os
import socket
import subprocess
import sys
import time
import urllib
from telnetlib import EC
from urllib.parse import urlparse, urljoin

import pymysql
import requests
import urllib3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from information_collection import Information
from similarity.imageSimilarity import image_similarity
from similarity.structureSimilarity import structure_similarity
from similarity.textSimilarity import calculate_sourcecode_similarity
from sql.ConnectDB import get_mysql_conn

from sql.website_information_database import get_secondary_links, get_tertiary_links

# from similarity.imageSimilarity import image_similarity
# from similarity.structureSimilarity import structure_similarity
# from similarity.textSimilarity import get_webpage_similarity

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "max-age=0",
    "cookie": "__yjs_duid=1_06d53fe303b699751bfabe6b9489aa101667713733022; Hm_lvt_c59f2e992a863c2744e1ba985abaea6c=1667713735; zkhanecookieclassrecord=%2C68%2C54%2C; Hm_lpvt_c59f2e992a863c2744e1ba985abaea6c=1667713739",
    "if-modified-since": "Fri, 04 Nov 2022 16:27:59 GMT",
    "referer": "https://pic.netbian.com/shoujibizhi/",
    "sec-ch-ua": "\";Not A Brand\";v=\"99\", \"Chromium\";v=\"94\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 Core/1.94.178.400 QQBrowser/11.2.5170.400",
    'If-None-Natch': '',
    'If-Modified-Since': ''
}

conn = get_mysql_conn()


def ipv6_family():
    return socket.AF_INET6


def ipv4_family():
    return socket.AF_INET


def test_server(url, port, use_https=False):
    requests.packages.urllib3.util.connection.allowed_gai_family = ipv6_family  # 切换socket至ipv6环境
    try:
        protocol = "https" if use_https else "http"
        full_url = f"{protocol}://{url}:{port}"
        print(full_url)
        response = requests.get(full_url, headers=headers, verify=False)

        if response.status_code == 200:
            print(f"成功从{url} 的服务端口 {port} 发起{protocol}请求，并得到响应。")
            return 1
        else:
            print(response.status_code)
            print(f"从{url} 的服务端口 {port} 发起{protocol}请求，但未得到有效响应。")
            return 0
    except Exception as e:
        print(f"发生异常：{e}")
        return 0


# 尝试通过IPv6解析网站
def try_ipv6_resolution(domain):
    try:
        # 获取地址信息，其中AF_INET6指定了IPv6地址族
        address_info = socket.getaddrinfo(domain, None, socket.AF_INET6)
        # 如果不为空，则表示存在IPv6地址
        if address_info:
            return 1
    except socket.gaierror as e:
        # 如果getaddrinfo引发异常，可能是域名不存在或不支持IPv6解析
        pass
    return 0


# 尝试通过IPv6访问网站
def try_ipv6_access(domain):
    try:
        # 创建一个IPv6的URL
        url = f'https://{domain}'
        # 使用urllib请求URL内容
        response = urllib.request.urlopen(url)
        # 读取响应内容
        content = response.read()
        print(f"成功通过IPv6访问 {domain}，响应内容长度：{len(content)}")
        return 1
    except urllib.error.URLError as e:
        print(f"无法通过IPv6访问 {domain}，错误信息：{e.reason}")
        return 0


# 测试建立ipv6连接成功率
def get_ipv6_connectivity(links):
    success_count = 0
    requests.packages.urllib3.util.connection.allowed_gai_family = ipv6_family  # 切换socket至ipv6环境
    for link in links:
        try:
            response = requests.get(link, timeout=10, headers=headers, verify=False)

            if response.status_code == 200:
                success_count += 1
                print(f"成功访问 {link}")
            else:
                print(f"访问 {link} 失败")
        except Exception as e:
            print(f"访问 {link} 出现异常: {e}")
        s = requests.session()
        s.keep_alive = False
    if len(links) > 0:
        success_rate = (success_count / len(links)) * 100
    else:
        success_rate = 0
    return success_rate


class IPv6SupportDegree:
    def __init__(self, ip_address):
        self.domain = ip_address
        self.ip_address = "https://" + self.domain
        self.support_degree = 0
        self.ipv6_resolution = 0
        self.ipv6_http_server = 0
        self.ipv6_https_server = 0
        self.dual_stack = 0
        self.ipv6_connectivity = 0
        self.ipv6_sub_connectivity = 0
        self.ipv6_third_connectivity = 0
        self.ipv6_stablity = 0
        self.ipv6_authorization = 0
        self.ipv4_dns_delay = 0
        self.ipv6_dns_delay = 0
        self.dns_delay_ratio = 0
        self.ipv4_tcp_delay = 0
        self.ipv6_tcp_delay = 0
        self.tcp_delay_ratio = 0
        self.ipv4_ack_delay = 0
        self.ipv6_ack_delay = 0
        self.ack_delay_ratio = 0
        self.ipv4_delay = 0
        self.ipv6_delay = 0
        self.delay_ratio = 0
        self.text_similarity = 0
        self.image_similarity = 0
        self.structure_similarity = 0

    # 1. 首页是否可以访问
    """
    向网站ipv6地址的服务端口发起http/https请求，测试是否得到应答
    """

    def test_ipv6_resolution(self):
        self.ipv6_resolution = try_ipv6_resolution(self.domain)

    def test_ipv6_server(self, http_port=80, https_port=443):
        self.ipv6_http_server = test_server(self.domain, http_port)  # 发起HTTP请求测试
        # 若要测试HTTPS请求，将use_https参数设为True
        self.ipv6_https_server = test_server(self.domain, https_port, use_https=True)

    # 2. 网站支持ipv4和ipv6双栈
    """
    根据网站域名，判断是否可以获取到网站的ipv4地址和ipv6地址
    """

    def check_dual_stack_support(self):
        try:
            ipv4_address = socket.getaddrinfo(self.domain, None, socket.AF_INET)
            ipv6_address = socket.getaddrinfo(self.domain, None, socket.AF_INET6)

            if ipv4_address and ipv6_address:
                self.dual_stack = 3
                return "Both IPv4 and IPv6 are supported."
            elif ipv4_address:
                self.dual_stack = 1
                return "IPv4 is supported, but IPv6 is not supported."
            elif ipv6_address:
                self.dual_stack = 2
                return "IPv6 is supported, but IPv4 is not supported."
            else:
                return 0
        except socket.gaierror:
            return "Error occurred while resolving addresses."

    # 3. ipv6连通性
    """
    在ipv6环境下，连续多次（大于10次）访问网站，每次访问间隔不大于300秒，计算ipv6连通性
    尝试使用不同的dns解析服务器，重复测试
    成功次数/访问总数*100%
    """

    # 定义目标网站和访问次数
    def test_ipv6_connectivity_dns(self, total_attempts, dns_servers, interval=300):
        success_count = 0
        requests.packages.urllib3.util.connection.allowed_gai_family = ipv6_family  # 切换socket至ipv6环境
        for dns_server in dns_servers:
            for _ in range(total_attempts):
                try:
                    # 设置DNS服务器
                    socket.create_connection((dns_server, 53), timeout=2)
                    socket.setdefaulttimeout(2)

                    # 发起HTTP请求
                    response = requests.get(self.ip_address, headers=headers, verify=False)
                    if response.status_code == 200:
                        success_count += 1
                        print(f"成功访问 {self.domain}，使用DNS服务器 {dns_server}")
                    else:
                        print(f"访问 {self.domain} 失败，使用DNS服务器 {dns_server}")
                except Exception as e:
                    print(f"访问 {self.domain} 出现异常，使用DNS服务器 {dns_server}: {e}")

                time.sleep(interval)  # 每次访问间隔300秒

        self.ipv6_connectivity = (success_count / (total_attempts * len(dns_servers))) * 100
        print(f"成功率为: {self.ipv6_connectivity}%")

    # 测试程序
    # target_url = 'http://www.tsinghua.edu.cn'
    # total_attempts = 15
    # dns_servers = ['2001:4860:4860::8888', '2620:0:ccc::2', '2620:0:ccd::2']
    #
    # test_ipv6_connectivity_dns(target_url, total_attempts, dns_servers)

    # 4. 二级链接ipv6连通性
    """
    在ipv6环境下，依次访问网站的二级链接，并记录访问成功的次数，计算二级链接连通性
    成功次数/二级链接总数*100%
    """

    def test_ipv6_sub_connectivity(self):
        links = get_secondary_links(conn, self.domain)
        self.ipv6_sub_connectivity = get_ipv6_connectivity(links)
        print(f"二级链接连通性成功率为: {self.ipv6_sub_connectivity}%")

    # 5. 三级链接ipv6连通性
    """
    在ipv6环境下，依次访问网站的三级链接，并记录访问成功的次数，计算三级链接连通性
    成功次数/三级链接总数*100%
    """

    def test_ipv6_third_connectivity(self):
        links = get_tertiary_links(conn, self.domain)
        self.ipv6_third_connectivity = get_ipv6_connectivity(links)
        print(f"三级链接连通性成功率为: {self.ipv6_third_connectivity}%")

    # 6. ipv6访问稳定性
    """
    按照一定的访问时间间隔（不大于300秒），访问周期不低于24小时，对网站进行ipv6访问，计算访问成功率
    """

    def test_ipv6_stablity(self, total_time=24, interval=300):
        success_count = 0
        total_count = 0
        start_time = time.time()
        requests.packages.urllib3.util.connection.allowed_gai_family = ipv6_family  # 切换socket至ipv6环境
        while time.time() - start_time < total_time * 60 * 60:  # 24小时为一个周期
            try:
                response = requests.get(self.ip_address, timeout=10, headers=headers, verify=False)
                if response.status_code == 200:
                    success_count += 1
                    print(f"成功访问 {self.ip_address}")
                else:
                    print(f"访问 {self.ip_address} 失败")
            except requests.exceptions.RequestException as e:
                print(f"访问 {self.ip_address} 出现异常: {e}")
            total_count += 1
            time.sleep(interval)  # 访问时间间隔不大于300秒
        self.ipv6_stablity = (success_count / total_count) * 100
        print(f"访问成功率为: {self.ipv6_stablity}%")

    # 7. ipv4域名解析时延
    """
    记录发起DNS解析域名请求，返回ipv4地址的时延
    测试至少10次，每次间隔不大于300秒，计算平均时延
    """

    def measure_dns_delay(self, num_tests, interval) -> float:
        """
        测量解析指定域名到IPv4地址的平均时延。

        :param hostname: 要解析的域名。
        :param num_tests: 测试次数，默认为10次。
        :param interval: 每次测试的间隔时间（秒），默认为5秒。
        :return: 平均时延（秒）。
        """
        delays = []
        for _ in range(num_tests):
            start_time = time.time()
            # 解析域名，注意只取IPv4地址
            socket.getaddrinfo(self.domain, None, family=socket.AF_INET)
            end_time = time.time()
            delay = end_time - start_time
            delays.append(delay)
            print(f"解析 {self.domain} 花费时间：{delay}秒")
            if _ < num_tests - 1:
                time.sleep(interval)
        average_delay = sum(delays) / num_tests
        self.ipv4_dns_delay = average_delay
        return average_delay

    # 使用示例
    # hostname = 'www.baidu.com'  # 可以更换为你想要测试的域名
    # num_tests = 10  # 测试次数
    # interval = 5  # 每次测试的间隔时间（秒）
    # average_delay = measure_dns_delay_7(hostname, num_tests, interval)
    # print(f"\n平均解析时延：{average_delay}秒")

    # 8. ipv6域名解析时延
    """
    记录DNS解析域名，返回ipv4地址的时延
    测试至少10次，每次间隔不大于300秒，计算平均时延
    """

    def measure_dns_delay_ipv6(self, num_tests, interval) -> float:
        """
        测量解析指定域名到IPv6地址的平均时延。

        :param hostname: 要解析的域名。
        :param num_tests: 测试次数，默认为10次。
        :param interval: 每次测试的间隔时间（秒），默认为5秒。
        :return: 平均时延（秒）。
        """
        delays = []
        for _ in range(num_tests):
            start_time = time.time()
            # 解析域名，指定IPv6地址族
            socket.getaddrinfo(self.domain, None, family=socket.AF_INET6)
            end_time = time.time()
            delay = end_time - start_time
            delays.append(delay)
            print(f"解析 {self.ip_address} 到IPv6地址花费时间：{delay}秒")
            if _ < num_tests - 1:
                time.sleep(interval)
        average_delay = sum(delays) / num_tests
        self.ipv6_dns_delay = average_delay
        return average_delay

    # 使用示例
    # hostname = 'www.google.com'  # 可以更换为你想要测试的域名
    # num_tests = 10  # 测试次数
    # interval = 5  # 每次测试的间隔时间（秒）
    # average_delay = measure_dns_delay_ipv6_8(hostname, num_tests, interval)
    # print(f"\n平均解析到IPv6地址的时延：{average_delay}秒")

    # 9. 计算是否满足域名解析时延指标
    """
    ipv6域名解析时延/ipv4域名解析时延 - 1 <= 0.2
    """

    def check_dns_delay_criteria(self, num_tests, interval) -> bool:
        """
        检查IPv6域名解析时延是否满足相对于IPv4增加不超过20%的条件。

        :param hostname: 要检查的域名。
        :param num_tests: 测试次数，默认为10次。
        :param interval: 每次测试的间隔时间（秒），默认为5秒。
        :return: 布尔值，True表示满足条件，False表示不满足。
        """
        # 测量IPv4解析时延
        ipv4_delay = self.measure_dns_delay(num_tests, interval)
        print(f"IPv4平均解析时延：{ipv4_delay}秒")

        # 测量IPv6解析时延
        ipv6_delay = self.measure_dns_delay_ipv6(num_tests, interval)
        print(f"IPv6平均解析时延：{ipv6_delay}秒")

        # 计算时延比例并判断是否满足条件
        delay_ratio = ipv6_delay / ipv4_delay - 1
        print(f"IPv6/IPv4解析时延比例 - 1：{delay_ratio}")
        self.dns_delay_ratio = delay_ratio
        return delay_ratio <= 0.2

    # 使用示例
    # hostname = 'www.google.com'  # 可以更换为你想要测试的域名
    # if check_dns_delay_criteria_9(hostname):
    #     print(f"{hostname} 满足域名解析时延指标。")
    # else:
    #     print(f"{hostname} 不满足域名解析时延指标。")

    # 10. ipv4环境下TCP建立时延
    """
    计算ipv4环境下，TCP三次握手建立连接的时延
    测试至少10次，每次间隔不大于300秒，计算平均时延
    """

    def measure_tcp_handshake_delay_ipv4(self, num_tests, interval, port: int = 80) -> float:
        """
        测量IPv4环境下TCP三次握手的平均时延。

        :param hostname: 目标服务器的域名。
        :param port: 目标服务器的端口号。
        :param num_tests: 测试次数，默认为10次。
        :param interval: 每次测试的间隔时间（秒），默认为5秒。
        :return: 平均时延（秒）。
        """
        delays = []  # 存储每次测试的时延
        for _ in range(num_tests):
            try:
                # 解析域名获取IPv4地址
                ipv4_addr_info = socket.getaddrinfo(self.domain, port, socket.AF_INET,
                                                    socket.SOCK_STREAM)
                ipv4_addr = ipv4_addr_info[0][4][0]  # 获取第一个返回的IPv4地址
                start_time = time.time()  # 开始尝试连接的时间
                # 使用IPv4地址和指定端口创建TCP连接
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((ipv4_addr, port))
                    end_time = time.time()  # 连接成功的时间
                    delays.append(end_time - start_time)
            except Exception as e:
                print(f"连接错误: {e}")
                continue  # 如果连接失败，跳过这次测试
            finally:
                print(f"TCP三次握手时延：{delays[-1]}秒" if delays else "测试失败，未记录时延。")
                if _ < num_tests - 1:
                    time.sleep(interval)  # 在测试之间等待
        average_delay = sum(delays) / len(delays) if delays else float('inf')
        self.ipv4_tcp_delay = average_delay
        return average_delay

    # 使用示例
    # hostname = 'www.baidu.com'  # 测试的域名
    # port = 80  # HTTP默认端口
    # average_delay = measure_tcp_handshake_delay_ipv4_10(hostname, port)
    # print(f"\n平均ipv4下TCP三次握手时延：{average_delay}秒")

    # 11. ipv6环境下TCP建立时延
    """
    计算ipv6环境下，TCP三次握手建立连接的时延
    测试至少10次，每次间隔不大于300秒，计算平均时延
    """

    def measure_tcp_handshake_delay_ipv6(self, num_tests, interval, port: int = 80) -> float:
        """
        测量IPv6环境下TCP三次握手的平均时延。

        :param hostname: 目标服务器的域名。
        :param port: 目标服务器的端口号。
        :param num_tests: 测试次数，默认为10次。
        :param interval: 每次测试的间隔时间（秒），默认为5秒。
        :return: 平均时延（秒）。
        """
        delays = []  # 存储每次测试的时延
        for _ in range(num_tests):
            try:
                # 解析域名获取IPv6地址
                ipv6_addr_info = socket.getaddrinfo(self.domain, port, socket.AF_INET6,
                                                    socket.SOCK_STREAM)
                ipv6_addr = ipv6_addr_info[0][4][0]  # 获取第一个返回的IPv6地址
                start_time = time.time()  # 开始尝试连接的时间
                # 使用IPv6地址和指定端口创建TCP连接
                with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as sock:
                    sock.connect((ipv6_addr, port))
                    end_time = time.time()  # 连接成功的时间
                    delays.append(end_time - start_time)
            except Exception as e:
                print(f"连接错误: {e}")
                continue  # 如果连接失败，跳过这次测试
            finally:
                print(f"TCP三次握手时延：{delays[-1]}秒" if delays else "测试失败，未记录时延。")
                if _ < num_tests - 1:
                    time.sleep(interval)  # 在测试之间等待
        average_delay = sum(delays) / len(delays) if delays else float('inf')
        self.ipv6_tcp_delay = average_delay
        return average_delay

    # # 使用示例
    # hostname = 'www.baidu.com'  # 测试的域名
    # port = 80  # HTTP默认端口
    # average_delay = measure_tcp_handshake_delay_ipv6_11(hostname, port)
    # print(f"\n平均ipv4下TCP三次握手时延：{average_delay}秒")

    # 12. 计算是否满足TCP建立解析时延指标
    """
    ipv6建立时延/ipv4建立时延 - 1 <= 0.2
    """

    def check_tcp_handshake_delay_criteria(self, num_tests, interval, port: int = 80) -> bool:
        """
        检查IPv6 TCP建立时延是否满足相对于IPv4增加不超过20%的条件。

        :param hostname: 目标服务器的域名。
        :param port: 目标服务器的端口号。
        :param num_tests: 测试次数，默认为10次。
        :param interval: 每次测试的间隔时间（秒），默认为5秒。
        :return: 布尔值，True表示满足条件，False表示不满足。
        """
        # 测量IPv4 TCP建立时延
        ipv4_delay = self.measure_tcp_handshake_delay_ipv4(port, num_tests, interval)
        print(f"IPv4 TCP建立平均时延：{ipv4_delay}秒")

        # 测量IPv6 TCP建立时延
        ipv6_delay = self.measure_tcp_handshake_delay_ipv6(port, num_tests, interval)
        print(f"IPv6 TCP建立平均时延：{ipv6_delay}秒")

        # 计算时延比例并判断是否满足条件
        delay_ratio = ipv6_delay / ipv4_delay - 1
        print(f"IPv6/IPv4 TCP建立时延比例 - 1：{delay_ratio}")
        return delay_ratio <= 0.2

    # 13. ipv4环境下服务器响应首包时延
    """
    计算ipv4环境下，计算GET请求下收到第一个ACK响应包的时延
    测试至少10次，每次间隔不大于300秒，计算平均时延
    """

    def calculate_average_ack_delay_ipv4(self, testnum, interval):
        total_delay = 0
        socket.AF_INET6 = False  # 设置IPv4地址
        for i in range(testnum):
            start_time = time.time()
            response = requests.get(self.ip_address)
            end_time = time.time()

            ack_delay = end_time - start_time
            total_delay += ack_delay

            print(f"Test {i + 1}: ACK delay = {ack_delay} seconds")

            if i != testnum - 1:
                time.sleep(interval)  # 每次测试间隔不大于300秒

        average_delay = total_delay / testnum
        print(f"\nAverage ACK delay = {average_delay} seconds")
        self.ipv4_ack_delay = average_delay
        return average_delay

    # 14. ipv6环境下服务器响应首包时延
    """
    计算ipv6环境下，计算GET请求下收到第一个ACK响应包的时延
    测试至少10次，每次间隔不大于300秒，计算平均时延
    """

    def calculate_average_ack_delay_ipv6(self, testnum, interval):
        total_delay = 0
        try:
            # 设置IPv6地址
            socket.AF_INET = None
            for i in range(testnum):
                try:
                    start_time = time.time()
                    response = requests.get(self.ip_address)
                    end_time = time.time()

                    ack_delay = end_time - start_time
                    total_delay += ack_delay

                    print(f"Test {i + 1}: ACK delay = {ack_delay} seconds")

                    if i != testnum - 1:
                        time.sleep(interval)  # 每次测试间隔不大于300秒

                except requests.exceptions.RequestException as e:
                    print(f"RequestException occurred during test {i + 1}: {str(e)}")

        except Exception as e:
            print(f"Exception occurred: {str(e)}")

        average_delay = total_delay / testnum
        print(f"\nAverage ACK delay = {average_delay} seconds")
        self.ipv6_ack_delay = average_delay
        return average_delay

    # 15. 计算是否满足服务器响应首包时延
    """
    ipv6响应时延/ipv4响应时延 - 1 <= 0.2
    """

    def check_response_delay_ratio(self, testnum, interval):
        try:
            ratio = self.calculate_average_ack_delay_ipv6(testnum, interval) / self.calculate_average_ack_delay_ipv4(
                testnum, interval) - 1
            print(f"\n比例 = {ratio}")

            if ratio <= 0.2:
                print("满足条件")
            else:
                print("不满足条件")
            self.ack_delay_ratio = ratio
            return ratio

        except ZeroDivisionError:
            print("除数为零错误：无法计算比例")
            return None

        except Exception as e:
            print(f"异常发生：{str(e)}")
            return None

    # 16. ipv4环境下服务器响应首页时延
    """
    计算ipv4环境下，计算发起网页请求到用户终端完整呈现网站内容之间的时延
    测试至少10次，每次间隔不大于300秒，计算平均时延
    """

    # 16.ipv4环境下服务器响应首页时延
    def ipv4delay(self, num_tests, interval):
        def measure_page_load_time(url):
            try:
                chrome_options = webdriver.ChromeOptions()
                # 2> 添加无头参数r,一定要使用无头模式，不然截不了全页面，只能截到你电脑的高度
                chrome_options.add_argument('--headless')
                # # 3> 为了解决一些莫名其妙的问题关闭 GPU 计算
                chrome_options.add_argument('--disable-gpu')
                # # 4> 为了解决一些莫名其妙的问题浏览器不动
                chrome_options.add_argument('--no-sandbox')
                driver = webdriver.Remote("http://127.0.0.1:4444", options=chrome_options)

                # 记录开始时间
                start_time = time.time()

                driver.get(url)  # 打开网页

                # 等待页面加载完成
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

                # 等待页面所有资源加载完成
                WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'img')))

                # 记录结束时间
                end_time = time.time()

                # 关闭浏览器
                driver.quit()

                # 计算页面加载时间
                load_time = end_time - start_time
                return load_time

            except Exception as e:
                print(f"异常发生：{str(e)}")
                return None

        # 进行多次测试
        total_load_time = 0
        for i in range(num_tests):
            load_time = measure_page_load_time(self.ip_address)
            if load_time is not None:
                total_load_time += load_time
                print(f"第 {i + 1} 次测试：{load_time} 秒")
            if i < num_tests - 1:
                time.sleep(interval)

        # 计算平均加载时间
        average_load_time = total_load_time / num_tests
        print(f"\n平均加载时间：{average_load_time} 秒")
        self.ipv4_delay = average_load_time
        return average_load_time

    # 17. ipv6环境下服务器响应首页时延
    """
    计算ipv6环境下，计算发起网页请求到用户终端完整呈现网站内容之间的时延
    测试至少10次，每次间隔不大于300秒，计算平均时延
    """

    def ipv6delay(self, num_tests, interval):
        def measure_page_load_time(url):
            try:
                chrome_options = Options()
                chrome_options.add_argument('--headless')
                # # 3> 为了解决一些莫名其妙的问题关闭 GPU 计算
                chrome_options.add_argument('--disable-gpu')
                # # 4> 为了解决一些莫名其妙的问题浏览器不动
                chrome_options.add_argument('--no-sandbox')
                service = Service(executable_path='/usr/bin/chromedriver')
                driver = webdriver.Chrome(service=service, options=chrome_options)
                # 记录开始时间
                start_time = time.time()

                driver.get(url)  # 打开网页

                # 等待页面加载完成
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

                # 等待页面所有资源加载完成
                WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'img')))

                # 记录结束时间
                end_time = time.time()

                # 关闭浏览器
                driver.quit()

                # 计算页面加载时间
                load_time = end_time - start_time
                return load_time

            except Exception as e:
                print(f"异常发生：{str(e)}")
                return None

        # 进行多次测试
        total_load_time = 0
        for i in range(num_tests):
            load_time = measure_page_load_time(self.ip_address)
            if load_time is not None:
                total_load_time += load_time
                print(f"第 {i + 1} 次测试：{load_time} 秒")
            if i < num_tests - 1:
                time.sleep(interval)

        # 计算平均加载时间
        average_load_time = total_load_time / num_tests
        print(f"\n平均加载时间：{average_load_time} 秒")
        self.ipv6_delay = average_load_time
        return average_load_time

    # 18. 计算是否满足服务器响应首页时延
    """
    ipv6首页时延/ipv4首页时延 - 1 <= 0.2
    """

    def check_homepage_delay(self, test_num, interval):
        try:
            ratio = (self.ipv6delay(test_num, interval) / self.ipv4delay(test_num, interval)) - 1

            if ratio <= 0.2:
                print("满足服务器响应首页时延条件")
            else:
                print("不满足服务器响应首页时延条件")
            self.delay_ratio = ratio
            return ratio

        except ZeroDivisionError:
            print("除数为零错误：无法计算比例")
            return None

        except Exception as e:
            print(f"异常发生：{str(e)}")
            return None

    # 19. ipv4和ipv6环境下，页面截图之间的相似性
    """
    根据ipv4和ipv6环境下的网页截图，计算图片相似度。
    """

    def calc_image_similarity(self):
        ipv4Img = "IPv4/ipv4." + self.domain + ".png"
        ipv6Img = "IPv6/ipv6." + self.domain + ".png"
        if os.path.exists(ipv4Img) and os.path.exists(ipv6Img):
            pic_similarity = image_similarity(ipv4Img, ipv6Img)
        else:
            pic_similarity = 0
        self.image_similarity = pic_similarity

    # 20. ipv4和ipv6环境下，页面文本内容的相似性
    """
    分别从ipv4网页源代码和ipv6网页源代码中提取所有文字内容，计算文本相似度
    也可分别计算网站网页正文，网站标题等等不同区域的文本相似度，并加权获得最终的文本相似度
    """

    def calc_text_similarity(self, conn: pymysql.connections.Connection):
        text_similarity = 0
        cursor = conn.cursor()
        query_sql = "SELECT ipv4_source_code,ipv6_source_code FROM website_information WHERE domain = %s"
        cursor.execute(query_sql, self.domain)
        result = cursor.fetchall()
        for tuple_element in result:
            if tuple_element[0] and tuple_element[1]:
                text_similarity = calculate_sourcecode_similarity(tuple_element[0], tuple_element[1])
        self.text_similarity = text_similarity

    # 21. ipv4和ipv6环境下，页面结构的相似性
    """
    分别从ipv4网页源代码和ipv6网页源代码中提取所有HTML标签与出现频率，构造词频向量，计算相似度
    """

    def calc_text_structure_similarity(self, conn: pymysql.connections.Connection):
        cursor = conn.cursor()
        query_sql = "SELECT ipv4_source_code,ipv6_source_code FROM website_information WHERE domain = %s"
        cursor.execute(query_sql, self.domain)
        result = cursor.fetchall()
        text_structure_similarity = 0
        for tuple_element in result:
            if tuple_element[0] and tuple_element[1]:
                text_structure_similarity = structure_similarity(tuple_element[0], tuple_element[1])
        self.structure_similarity = text_structure_similarity

    # 22. ipv6域名授权体系
    """
    递归查询网站ipv6地址: dig -6 +trace AAAA [网站域名] @[ipv6递归解析器地址]
    返回网站ipv6地址说明具备ipv6域名授权体系
    """

    def calc_ipv6_authorization(self):
        # print(domain)
        if sys.platform.startswith("win"):
            cmd = ['dig', self.domain, 'AAAA', '+trace']
        else:
            cmd = ['dig', self.domain, '-6', 'AAAA', '+trace']
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = ""
        # 获取实时输出
        for line in iter(p.stdout.readline, b''):
            temp = line.decode('utf-8').strip()
            # print(temp)
            if temp.find(self.domain) != -1:
                result = temp
        # 等待命令执行完成
        p.wait()
        print(result)
        if result.find("AAAA") != -1:
            self.ipv6_authorization = 1
            print("authorization True")
        else:
            self.ipv6_authorization = 0
            print("authorization False")

    # 24. ipv6支持度计算
    """
    根据前面的计算结果，加权计算最终的ipv6支持度
    """

    def calc_ipv6(self, conn: pymysql.connections.Connection, test_num=10, interval=5):
        self.test_ipv6_resolution()
        self.test_ipv6_server()
        self.check_dual_stack_support()
        self.calc_ipv6_authorization()
        self.test_ipv6_sub_connectivity()
        self.test_ipv6_third_connectivity()
        self.calc_image_similarity()
        self.calc_text_structure_similarity(conn)
        self.calc_text_similarity(conn)
        self.check_tcp_handshake_delay_criteria(test_num, interval)
        self.check_response_delay_ratio(test_num, interval)
        self.check_homepage_delay(test_num, interval)
        self.check_dns_delay_criteria(test_num, interval)

        # 24小时
        # self.test_ipv6_connectivity_dns(15, ['2001:4860:4860::8888', '2620:0:ccc::2', '2620:0:ccd::2'], 300)
        # self.test_ipv6_stablity()
        self.support_degree = (
                                      self.ipv6_resolution + self.ipv6_http_server + self.ipv6_https_server + self.dual_stack + self.ipv6_connectivity +
                                      self.ipv6_sub_connectivity + self.ipv6_third_connectivity + self.ipv6_stablity +
                                      self.ipv6_authorization + 1 - self.dns_delay_ratio + 1 - self.tcp_delay_ratio +
                                      1 - self.ack_delay_ratio + 1 - self.delay_ratio + self.text_similarity +
                                      self.image_similarity + self.structure_similarity) / 16.0 * 100
