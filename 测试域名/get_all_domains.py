import os.path
import random

import requests
import json
import re
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}

#保存域名
def get_all_domains(url,outputfile):
    response = requests.get(url, headers=headers)
    response.encoding = response.apparent_encoding  # 会出现中文乱码
    soup = BeautifulSoup(response.content, 'lxml')
    td_elemetns=soup.find_all('a')
    domain_list=[]
    if td_elemetns:
        for domain_info in td_elemetns:
                domain=domain_info.text
                if re.match(r'^[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+$',domain):
                    print(domain)
                    domain_list.append(domain)
    print("domains个数：",len(domain_list))
    with open(outputfile,'w',encoding="utf-8") as fw:
        json.dump(domain_list,fw, indent=2, ensure_ascii=False)



def get_num_domains(num=20):
    url = "https://ipv6c.cngi.edu.cn/2021.do?cer2Date=2024%2F04%2F16&inputProv=&selectType=2&lineType=2"
    outputfile='domains.json'

    if not os.path.exists(outputfile):
        get_all_domains(url, outputfile)
    with open(outputfile, 'r', encoding="utf-8") as fr:
        domains_list = json.load(fr)
    select_domains = random.sample(domains_list, num)
    print("随机选择的域名：", select_domains)
    return select_domains

if __name__ == '__main__':
    select_domains_list=get_num_domains(30)#指定返回的域名个数





