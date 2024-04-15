import re
import ssl
from bs4 import BeautifulSoup
import socket
import jieba
from urllib.parse import urlparse
from simhash import Simhash

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
    'If-Modified-Since': '',
    'Connection': 'close'
}


# '''
# 输出：获得当前主机ipv4地址
# '''
# def get_ipv4_address():
#     return socket.gethostbyname(socket.gethostname())
#
# '''
# 输出：获得当前主机ipv6地址
# '''
# def get_ipv6_address():
#     return [l for l in ([ip for ip in socket.getaddrinfo(socket.gethostname(), None) if ip[0] == socket.AF_INET6])][0][4][0]
def get_headers(headers, url):
    header_dict = {}
    header_list = headers.split("\r\n")
    for i in range(0, len(header_list)):
        if i == 0:
            if len(header_list[0].split(" ")) > 2:
                header_dict['schema'], header_dict['status_code'] = header_list[0].split(" ")[:2]

        else:
            k, v = header_list[i].split(":", 1)
            header_dict[k] = v.strip()
    return header_dict


def process_headers(headers_dict, url):
    location = headers_dict['Location']
    if location.startswith('/'):
        location = url + location
    print("原地址:", url)
    print("访问新地址：", location)
    return location


# 获得网页文本内容
def get_text(response):
    soup = BeautifulSoup(response, 'html.parser')
    text = soup.get_text(strip=True, separator='\n')
    return text


# 获得网页内容
def fetch_webpage_content(url, use_ipv6=False, access=True):
    # ip_address = get_ipv6_address() if use_ipv6 else get_ipv4_address()
    # print(f"Using {'IPv6' if use_ipv6 else 'IPv4'} address: {ip_address}")
    parsed_url = urlparse(url)
    path = parsed_url.path
    scheme = parsed_url.scheme
    host = parsed_url.hostname
    port = 443 if scheme == 'https' else 80
    try:
        if use_ipv6:
            try:
                ipv6_addrinfo = socket.getaddrinfo(host, 0, socket.AF_INET6)
            except Exception as e:
                print("不支持ipv6")
            s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)  # IPV6访问
            ip_port = (host, port, 0, 0)

        else:
            try:
                ipv4_addrinfo = socket.getaddrinfo(host, 0, socket.AF_INET)
            except Exception as e:
                print("不支持ipv4")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # IPV4访问
            ip_port = (host, port)

        if scheme == 'https':
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.check_hostname = False  # 禁用主机名验证
            context.verify_mode = ssl.CERT_NONE  # 忽略证书验证
            s = context.wrap_socket(s, server_hostname=host)
            # s = ssl.wrap_socket(s, cert_reqs=ssl.CERT_NONE)
        s.connect(ip_port)
        print("我的IP地址：", s.getsockname())
        print("建立连接的远程服务器地址:", s.getpeername())

        s.send("GET {} HTTP/1.1\r\nHost:{}\r\nConnection:close\r\n\r\n".format(path, host).encode("utf-8"))

        # 接收网页文本内容
        response = b""
        while True:
            data = s.recv(4096)
            if not data:
                break
            response += data
        s.close()
        try:
            # 首先尝试使用UTF-8解码
            content = response.decode('utf-8', errors='ignore')
        except UnicodeDecodeError:
            print('不支持utf-8解码!!!')
        html_header, html_data = content.split("\r\n\r\n", 1)
        header_dict = get_headers(html_header, url)
        if header_dict['status_code'] in ['301', '302', '303', '307', '308']:
            new_url = process_headers(header_dict, url, )  # 响应头、响应体
            html_data = fetch_webpage_content(new_url, use_ipv6, access=False)

        return html_data
    except socket.gaierror as e:
        print("地址解析错误:", e)
    except socket.error as e:
        print("连接错误:", e)
    except Exception as e:
        print(e)


# 对文本进行分词，传给Simhash
def process_text(text):
    segments = jieba.cut(text, cut_all=False)
    return segments


# 计算IPV4文本和IPV6文本内容相似度，计算方法是Simhash，返回similarity （100.00%）
def calculate_similarity(ipv4_text, ipv6_text):
    ipv4_text = process_text(ipv4_text)  # 自己分词
    ipv6_text = process_text(ipv6_text)
    ipv4_simhash = Simhash(ipv4_text, f=128)  # 在文本长度较短或者相似度较高的情况下，可能会导致相似度计算的结果不够稳定。
    ipv6_simhash = Simhash(ipv6_text, f=128)
    distance = ipv4_simhash.distance(ipv6_simhash)  # 计算汉明距离
    similarity = "{:.2f}%".format((1 - distance / 128) * 100)
    return similarity


''' 20. ipv4和ipv6环境下，页面文本内容的相似性:get_webpage_similarity(url) '''
'''
输入：url——网址
输出：IPV4和IPV6访问页面内容相似度——100.00%
'''


def get_webpage_similarity(url):
    print("IPV4访问:")
    ipv4_response = fetch_webpage_content(url, use_ipv6=False)  # 为了更新重定向后的url，避免再次解析
    if ipv4_response:  # IPV4访问
        ipv4_text = get_text(ipv4_response)
    else:
        print("IPV4访问失败!!!")
        return 0
    print("IPV6访问:")
    ipv6_response = fetch_webpage_content(url, use_ipv6=True)  # IPV6访问
    if ipv6_response:
        ipv6_text = get_text(ipv6_response)
    else:
        print("IPV6访问失败!!!")
        return 0
    similarity = calculate_similarity(ipv4_text, ipv6_text)
    print(f"网页{url}的IPV4访问和IPV6访问内容相似度为：{similarity}")
    return similarity

# if __name__ == '__main__':
#     url = "https://www.ucas.edu.cn/"#https://www.pumc.edu.cn/ IPV6可访问但是[WinError 10060] 由于连接方在一段时间后没有正确答复或连接的主机没有反应，连接尝试失败。
#     get_webpage_similarity(url)
