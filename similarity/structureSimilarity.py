from collections import Counter
from html.parser import HTMLParser
import numpy as np
from information_collection import Information
import urllib3
import socket
import requests
from urllib3.util import connection

requests.packages.urllib3.disable_warnings()
#
# USE_IPV6 = False
#
#
# def allowed_gai_family():
#     family = socket.AF_INET
#     if USE_IPV6:
#         family = socket.AF_INET6
#     return family
#
#
# original_allowed_gai_family = connection.allowed_gai_family
#
#
# def forced_ipv6_gai_family():
#     return socket.AF_INET6
#
#
# connection.allowed_gai_family = forced_ipv6_gai_family
#
# # 你的urllib3请求代码
# http = urllib3.PoolManager()
# response = http.request('GET', 'http://video.neu6.edu.cn/')
# url = "http://video.neu6.edu.cn/"
# response2 = requests.get(url)
#
# # 检查请求是否成功
# if response2.status_code == 200:
#     html2 = response2.text
#     print(html2)
# html2 = response2.text
# print(html2)
# html1 = response.data.decode('utf-8')


class TagExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)

    def handle_endtag(self, tag):
        self.tags.append(tag)


def structure_similarity(html1, html2):
    # 提取HTML1标签
    parser1 = TagExtractor()
    parser1.feed(html1)
    tags1 = Counter(parser1.tags)

    # 提取HTML2标签
    parser2 = TagExtractor()
    parser2.feed(html2)
    tags2 = Counter(parser2.tags)
    # 打印标签及频率
    print("IPv4 Tags:", tags1)
    print("IPv6 Tags:", tags2)
    # 构造向量
    tags_set = set(list(tags1.keys()) + list(tags2.keys()))
    vec1 = np.array([tags1.get(tag, 0) for tag in tags_set])
    vec2 = np.array([tags2.get(tag, 0) for tag in tags_set])
    # 计算余弦相似度
    cosine_similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    print("Cosine Similarity:", cosine_similarity)
