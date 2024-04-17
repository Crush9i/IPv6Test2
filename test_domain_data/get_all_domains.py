import os.path
import random

import requests
import json
import re
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}

#保存域名
def get_all_domains(url, output_domainfile,output_urlfile):
    response = requests.get(url, headers=headers)
    response.encoding = response.apparent_encoding  # 会出现中文乱码
    soup = BeautifulSoup(response.content, 'lxml')
    td_elemetns=soup.find_all('a')
    domain_list=[]
    link_list=[]
    if td_elemetns:
        for domain_info in td_elemetns:
                domain=domain_info.text
                if re.match(r'^[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+$',domain):
                    link=domain_info['href'].replace('http','https')+'/'
                    print(domain)
                    domain_list.append(domain)
                    link_list.append(link)
    print("domains个数：",len(domain_list))
    with open(output_domainfile,'w',encoding="utf-8") as fw:
        json.dump(domain_list,fw, indent=2, ensure_ascii=False)
    with open(output_urlfile,'w',encoding='utf-8') as f:
        json.dump(link_list,f,indent=2,ensure_ascii=False)




def get_num_domains(num=20):
    url = "https://ipv6c.cngi.edu.cn/2021.do?cer2Date=2024%2F04%2F16&inputProv=&selectType=2&lineType=2"
    output_domainfile='domains.json'
    output_urlfile='urls.json'
    if not os.path.exists(output_domainfile):
        get_all_domains(url, output_domainfile,output_urlfile)
    with open(output_domainfile, 'r', encoding="utf-8") as fr:
        domains_list = json.load(fr)
    with open(output_urlfile,'r', encoding="utf-8") as f:
        urls_list = json.load(f)
    select_domains = random.sample(domains_list, num)
    print("随机选择的域名：", select_domains)
    select_urls=random.sample(urls_list, num)
    print("随机选择的网址：", select_urls)
    return select_domains,select_urls

if __name__ == '__main__':
    select_domains_list,select_urls_links=get_num_domains(30)#指定返回的域名个数





