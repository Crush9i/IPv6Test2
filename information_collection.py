# -*- coding: utf-8 -*-
from urllib.parse import urlparse, urljoin
import urllib3
from chardet import UniversalDetector
from requests.adapters import HTTPAdapter
from selenium import webdriver
import time
from bs4 import BeautifulSoup
import socket
import requests
from fake_useragent import UserAgent
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
urllib3.disable_warnings()
s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=3))  # 访问http协议时，设置重传请求最多三次
s.mount('https://', HTTPAdapter(max_retries=3))  # 访问https协议时，设置重传请求最多三次
s.keep_alive = False
ua = UserAgent()

headers = {
    "User-Agent": ua.random,
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


def ipv6_family():
    return socket.AF_INET6


def ipv4_family():
    return socket.AF_INET


def get_links(ip_address):
    requests.packages.urllib3.util.connection.allowed_gai_family = ipv6_family  # 切换socket至ipv6环境
    try:
        # 发送GET请求到基础URL
        response = requests.get(ip_address, verify=False, headers=headers)
        response.raise_for_status()  # 如果请求失败，这将引发HTTPError异常
        # 使用BeautifulSoup解析HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')
        response.close()
        # 提取所有的<a>标签（链接）
        links = soup.find_all('a')
        # 过滤并收集二级链接
        secondary_links = []
        for link in links:
            href = link.get('href')
            if href and not href.startswith('#') and not href.startswith('http') and href.find(
                    "javascript") == -1 and href.find("@") == -1:  # 排除不完整的链接和已经是完整URL的链接
                # 使用urljoin来确保链接是相对于基础URL的
                full_url = urljoin(ip_address, href)
                secondary_links.append(full_url)
        secondary_links = list(set(secondary_links))
        return secondary_links
    except Exception as e:
        print(e)
        return []


class Information:
    def __init__(self, domain):
        self.domain = domain
        self.url = "https://" + domain
        self.supportIPv4 = False
        self.supportIPv6 = False
        self.secondary_links = []
        self.tertiary_links = []
        self.ipv4_address = None
        self.ipv6_address = None
        self.ipv4_code = None
        self.ipv6_code = None

    # 信息采集
    # 1. 判断网站是否支持ipv4，获取ipv4地址
    # 2. 判断网站是否支持ipv6，获取ipv6地址
    def get_address(self, useIPv6=False):
        address_list = []
        try:
            if useIPv6:
                addresses = socket.getaddrinfo(self.domain, None, socket.AF_INET6)
            else:
                addresses = socket.getaddrinfo(self.domain, None, socket.AF_INET)
            for address in addresses:
                address_list.append(address[4][0])
        # 如果出现异常，说明不支持ipv6
        except Exception as e:
            pass
        if useIPv6:
            if not address_list:
                print(f"{self.domain}不支持ipv6访问，不支持解析AAAA地址。")
            else:
                self.supportIPv6 = True
                self.ipv6_address = address_list
        else:
            if not address_list:
                print(f"{self.domain}不支持ipv4访问，不支持解析A地址。")
            else:
                self.supportIPv4 = True
                self.ipv4_address = address_list
        return address_list

    def get_web_code(self, useIPv6=False):
        print("start web code")
        if useIPv6:
            requests.packages.urllib3.util.connection.allowed_gai_family = ipv6_family
        else:
            requests.packages.urllib3.util.connection.allowed_gai_family = ipv4_family
        web_code = ""
        try:
            print(self.url)
            r = requests.get(self.url, verify=False, headers=headers)
            print(r.status_code)
            # print(r.encoding)
            detector = UniversalDetector()
            for line in r.iter_lines():
                detector.feed(line)
                if detector.done:
                    break
            encoding = detector.result['encoding']
            print(encoding)
            r.encoding = encoding
            # data = r.content
            # result = data
            # html_string = result.decode(encoding, 'ignore')
            # html_utf8_bytes = html_string.encode('utf-8')
            # html_utf8_string = html_utf8_bytes.decode('utf-8')
            # detector.close()
            # web_code = html_utf8_string
            web_code = r.content.decode(encoding)
            # web_code = r.text
            r.close()
            # print(web_code)
            if useIPv6:
                self.ipv6_code = web_code
                with open('source_ipv6.txt', 'w', encoding='utf-8') as f:
                    f.write(self.ipv6_code)
            else:
                self.ipv4_code = web_code
                with open('source_ipv4.txt', 'w', encoding='utf-8') as f:
                    f.write(self.ipv4_code)
        except Exception as e:
            print(e)
        return web_code

    # 5. 获取ipv4环境下网站截图 注：需要在单栈ipv4网络环境下运行
    def get_pic(self, path, useIPv6=False):
        print("start pic")
        try:
            if useIPv6:
                chrome_options = Options()
                chrome_options.add_argument('--headless')
                # # 3> 为了解决一些莫名其妙的问题关闭 GPU 计算
                chrome_options.add_argument('--disable-gpu')
                # # 4> 为了解决一些莫名其妙的问题浏览器不动
                chrome_options.add_argument('--no-sandbox')
                service = Service(executable_path='/usr/bin/chromedriver')
                driver = webdriver.Chrome(service=service, options=chrome_options)
               # driver = webdriver.Chrome(options=chrome_options)
            else:
                # 1> 获取chrome参数对象
                chrome_options = webdriver.ChromeOptions()
                # 2> 添加无头参数r,一定要使用无头模式，不然截不了全页面，只能截到你电脑的高度
                chrome_options.add_argument('--headless')
                # # 3> 为了解决一些莫名其妙的问题关闭 GPU 计算
                chrome_options.add_argument('--disable-gpu')
                # # 4> 为了解决一些莫名其妙的问题浏览器不动
                chrome_options.add_argument('--no-sandbox')
                driver = webdriver.Remote("http://127.0.0.1:4444", options=chrome_options)
            try:
                driver.get(self.url)
                driver.set_page_load_timeout(3)
                print('finish load ....')
                k = 1
                js_height = "return document.body.scrollHeight"
                height = driver.execute_script(js_height)
                while True:
                    if k * 500 < height:
                        js_move = "window.scrollTo(0,{})".format(k * 500)
                        print(js_move)
                        driver.execute_script(js_move)
                        time.sleep(0.2)
                        height = driver.execute_script(js_height)
                        k += 1
                    else:
                        break
                driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
                k = 1
                js_width = "return document.body.scrollWidth"
                width = driver.execute_script(js_width)
                while True:
                    if k * 500 < width:
                        js_move = "window.scrollTo({},0)".format(k * 500)
                        print(js_move)
                        driver.execute_script(js_move)
                        time.sleep(0.2)
                        width = driver.execute_script(js_width)
                        k += 1
                    else:
                        break
                driver.execute_script("window.scrollTo(document.body.scrollWidth,0)")
                time.sleep(0.2)
                # 直接截图截不全，调取最大网页截图， 获取网页宽高
                width = driver.execute_script("return document.body.scrollWidth")
                height = driver.execute_script("return document.body.scrollHeight")
                print(width, height)
                # 将浏览器的宽高设置成刚刚获取的宽高
                driver.set_window_size(width, height)
                if useIPv6:
                    png_path = path + '/IPv6/{}.png'.format('ipv6.' +self.domain)
                else:
                    png_path = path + '/IPv4/{}.png'.format('ipv4.' +self.domain)
                # 截图并关掉浏览器
                print(png_path)
                driver.save_screenshot(png_path)
            except Exception:
                driver.execute_script('window.stop()')
                print(driver.title)
            finally:
                driver.quit()
        except Exception as e:
            print(e)

    # 7. 从网页源代码中提取二级链接
    def get_secondary_links(self):
        self.secondary_links = get_links(self.url)
        return self.secondary_links

    # 8. 从网页源代码中提取三级链接
    def get_tertiary_links(self):
        for link in self.secondary_links:
            temp = get_links(link)
            self.tertiary_links.extend(temp)
        return self.tertiary_links
