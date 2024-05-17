# -*- coding: UTF-8 -*-
启动ipv6浏览器


java -Dwebdriver.chrome.driver=/usr/bin/chromedriver  -jar /opt/selenium/selenium-server.jar standalone --session-request-timeout 300 --session-retry-interval 15 --healthcheck-interval 120 --bind-host false --config /opt/selenium/config.toml --heartbeat-period 30 --reject-unsupported-caps false

java -Dwebdriver.chrome.driver=chromedriver -jar selenium-server-standalone-4.0.0-alpha-2.jar -role node -hub http://118.31.70.29:5544/grid/register

java -jar selenium-server-standalone-4.0.0-alpha-2.jar -port 5555  -role hub -host 0.0.0.0
chromedriver --port=5555 --whitelisted-ips="" --remote-debugging-port=5555  --enable-webgl --no-sandbox --disable-dev-shm-usage
启动ipv4浏览器
docker run -d -p 4444:4444 --shm-size=2g selenium/standalone-chrome


**1. 运行sql/setDatabase.py**<br>
将database_passwd = "180380zj" 更改为自己的mysql密码，ConnectDB.py中密码也要更改。<br>
运行后会创建ipv6test数据库<br>
**2. 运行main.py**<br>
实现在website_information中插入num个网址的网页信息<br>
**3.sql/support_degree_database.py**<br>
在sql/support_degree_database.py中写两个函数，分别是<br>
1）查询website_information表获得相关信息计算并将结果保存到ipv6_support_degree表中；<br>
2）查询ipv6_support_degree表返回结果。

