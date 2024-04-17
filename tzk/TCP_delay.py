import time
import socket
from urllib.parse import urlparse
import pymysql


def get_Hostname(url):
    if url.startswith("http"):
        return urlparse(url).hostname
    else:
        return url


class TCPHandshakeTester:
    def __init__(self, ip_address):
        self.ip_address = get_Hostname(ip_address)
        self.ipv4_tcp_delay = None
        self.ipv6_tcp_delay = None

    def measure_tcp_handshake_delay_ipv4(self, port: int = 80, num_tests: int = 10, interval: int = 5) -> float:
        """
        测量IPv4环境下TCP三次握手的平均时延。
        """
        delays = []
        for _ in range(num_tests):
            try:
                ipv4_addr_info = socket.getaddrinfo(self.ip_address, port, socket.AF_INET, socket.SOCK_STREAM)
                ipv4_addr = ipv4_addr_info[0][4][0]
                start_time = time.time()
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((ipv4_addr, port))
                    end_time = time.time()
                delays.append(end_time - start_time)
            except Exception as e:
                print(f"连接错误: {e}")
                continue
            finally:
                print(f"TCP三次握手时延：{delays[-1]}秒" if delays else "测试失败，未记录时延。")
                if _ < num_tests - 1:
                    time.sleep(interval)
        self.ipv4_tcp_delay = sum(delays) / len(delays) if delays else float('inf')
        return self.ipv4_tcp_delay

    def measure_tcp_handshake_delay_ipv6(self, port: int = 80, num_tests: int = 10, interval: int = 5) -> float:
        """
        测量IPv6环境下TCP三次握手的平均时延。
        """
        delays = []
        for _ in range(num_tests):
            try:
                ipv6_addr_info = socket.getaddrinfo(self.ip_address, port, socket.AF_INET6, socket.SOCK_STREAM)
                ipv6_addr = ipv6_addr_info[0][4][0]
                start_time = time.time()
                with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as sock:
                    sock.connect((ipv6_addr, port))
                    end_time = time.time()
                delays.append(end_time - start_time)
            except Exception as e:
                print(f"连接错误: {e}")
                continue
            finally:
                print(f"TCP三次握手时延：{delays[-1]}秒" if delays else "测试失败，未记录时延。")
                if _ < num_tests - 1:
                    time.sleep(interval)
        self.ipv6_tcp_delay = sum(delays) / len(delays) if delays else float('inf')
        return self.ipv6_tcp_delay

    def check_tcp_handshake_delay_criteria(self, port: int = 80, num_tests: int = 10, interval: int = 5) -> bool:
        """
        检查IPv6 TCP建立时延是否满足相对于IPv4增加不超过20%的条件。
        """
        ipv4_delay = self.measure_tcp_handshake_delay_ipv4(port, num_tests, interval)

        ipv6_delay = self.measure_tcp_handshake_delay_ipv6(port, num_tests, interval)

        delay_ratio = ipv6_delay / ipv4_delay - 1
        # print(f"IPv6/IPv4 TCP建立时延比例 - 1：{delay_ratio}")
        return delay_ratio


def update_support_degree(conn, domain, resolve_delay):
    sql = """UPDATE ipv6_support_degree SET tcp_establishment_resolution_delay = %s WHERE domain = %s"""
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
                tester = TCPHandshakeTester(domain_name)
                TCP_delay = tester.check_tcp_handshake_delay_criteria()
                update_support_degree(conn, domain_name, TCP_delay)
                row = cursor.fetchone()
    except Exception as e:
        print(f"查询失败: {e}")
