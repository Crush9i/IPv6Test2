import time
import socket
from urllib.parse import urlparse
import pymysql


# 获取主机名
def get_Hostname(url):
    if url.startswith("http"):
        ip_address = urlparse(url).hostname
    else:
        ip_address = url
    return ip_address


class DNSDelayTester:
    def __init__(self, ip_address):
        self.ip_address = get_Hostname(ip_address)
        self.ipv4_dns_delay = None
        self.ipv6_dns_delay = None
        self.dns_delay_ratio = None

    def measure_dns_delay(self, num_tests: int = 10, interval: int = 5) -> float:
        delays = []
        for _ in range(num_tests):
            start_time = time.time()
            socket.getaddrinfo(self.ip_address, None, family=socket.AF_INET)
            end_time = time.time()
            delay = end_time - start_time
            delays.append(delay)
            if _ < num_tests - 1:
                time.sleep(interval)
        self.ipv4_dns_delay = sum(delays) / num_tests
        return self.ipv4_dns_delay

    def measure_dns_delay_ipv6(self, num_tests: int = 10, interval: int = 5) -> float:
        delays = []
        for _ in range(num_tests):
            start_time = time.time()
            socket.getaddrinfo(self.ip_address, None, family=socket.AF_INET6)
            end_time = time.time()
            delay = end_time - start_time
            delays.append(delay)
            if _ < num_tests - 1:
                time.sleep(interval)
        self.ipv6_dns_delay = sum(delays) / num_tests
        return self.ipv6_dns_delay

    def check_dns_delay_criteria(self, num_tests: int = 10, interval: int = 5) -> bool:
        ipv4_delay = self.measure_dns_delay(num_tests, interval)
        ipv6_delay = self.measure_dns_delay_ipv6(num_tests, interval)
        delay_ratio = ipv6_delay / ipv4_delay - 1
        self.dns_delay_ratio = delay_ratio
        return delay_ratio


def update_support_degree(conn, domain, resolve_delay):
    sql = """UPDATE ipv6_support_degree SET resolve_delay = %s WHERE domain = %s"""
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (resolve_delay, domain))
            conn.commit()
    except Exception as e:
        print(f"更新失败: {e}")
        conn.rollback()


def fetch_and_print_domains(conn):
    sql = "SELECT domain FROM ipv6_support_degree"
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            row = cursor.fetchone()
            if row is None:
                print("没有找到任何域名。")
            while row:
                domain_name = row[0]
                tester = DNSDelayTester(domain_name)
                DNS_delay = tester.check_dns_delay_criteria()
                update_support_degree(conn, domain_name, DNS_delay)
                row = cursor.fetchone()
    except Exception as e:
        print(f"查询失败: {e}")

#
