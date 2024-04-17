#13
def calculate_average_ack_delay_ipv4(self, testnum):
    total_delay = 0
    socket.AF_INET6 = False  # 设置IPv4地址
    for i in range(testnum):
        try:
            start_time = time.time()
            response = requests.get(self.ip_address)
            end_time = time.time()

            ack_delay = end_time - start_time
            total_delay += ack_delay

            print(f"Test {i + 1}: ACK delay = {ack_delay} seconds")

            if i != testnum - 1:
                time.sleep(1)  # 每次测试间隔不大于300秒

        except Exception as e:
            print(f"Exception occurred during test {i + 1}: {str(e)}")

    average_delay = total_delay / testnum
    print(f"\nAverage ACK delay = {average_delay} seconds")
    return average_delay

#14
def calculate_average_ack_delay_ipv6(self, testnum):
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
                    time.sleep(1)  # 每次测试间隔不大于300秒

            except requests.exceptions.RequestException as e:
                print(f"RequestException occurred during test {i + 1}: {str(e)}")

    except Exception as e:
        print(f"Exception occurred: {str(e)}")

    average_delay = total_delay / testnum
    print(f"\nAverage ACK delay = {average_delay} seconds")
    return average_delay

#15
def check_response_delay_ratio(self, calculate_average_ack_delay_ipv4, calculate_average_ack_delay_ipv6):
    try:
        ratio = calculate_average_ack_delay_ipv6() / calculate_average_ack_delay_ipv4() - 1
        print(f"\n比例 = {ratio}")

        if ratio <= 0.2:
            print("满足条件")
        else:
            print("不满足条件")
        return ratio

    except ZeroDivisionError:
        print("除数为零错误：无法计算比例")
        return None

    except Exception as e:
        print(f"异常发生：{str(e)}")
        return None

#16
def ipv4delay(self, num_tests, interval):
    def measure_page_load_time(url):
        try:
            options = Options()
            options.headless = True  # 无头模式，不显示浏览器窗口
            options.add_argument('--disable-ipv6')  # 禁用 IPv6
            options.add_argument('--disable-extensions')  # 禁用扩展
            options.add_argument('--disable-plugins')  # 禁用插件
            driver = webdriver.Chrome(options=options)

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
    return average_load_time

#17
def ipv6delay(self, num_tests, interval):
    def measure_page_load_time(url):
        try:
            options = Options()
            options.headless = True  # 无头模式，不显示浏览器窗口

            driver = webdriver.Chrome(options=options)
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
    return average_load_time

#18
def check_homepage_delay(self, ipv6delay, ipv4delay):
    try:
        ratio = (ipv6delay / ipv4delay) - 1

        if ratio <= 0.2:
            print("满足服务器响应首页时延条件")
        else:
            print("不满足服务器响应首页时延条件")
        return ratio

    except ZeroDivisionError:
        print("除数为零错误：无法计算比例")
        return None

    except Exception as e:
        print(f"异常发生：{str(e)}")
        return None

#13-18数据库指令
#存入server_responds_first_packet_delay:  服务器响应首包时延指标，浮点类型
def save_average_ack_delay(conn: pymysql.connections.Connection, domain='www.tsinghua.edu.cn'):
    cursor = conn.cursor()
    save_sql = """INSERT INTO ipv6_support_degree (domain, server_responds_first_packet_delay) VALUES (%s, %f) ON DUPLICATE KEY UPDATE server_responds_first_packet_delay = VALUES(server_responds_first_packet_delay)"""
    packet_ratio = IPv6SupportDegree('www.tsinghua.edu.cn')
    cursor.execute(save_sql, (domain,packet_ratio.check_response_delay_ratio(packet_ratio.calculate_average_ack_delay_ipv4,packet_ratio.calculate_average_ack_delay_ipv6)))
    conn.commit()


#存入server_responds_first_page_delay:   服务器响应首页时延指标，浮点类型
def save_average_page_delay(conn: pymysql.connections.Connection, domain='www.tsinghua.edu.cn'):
    cursor = conn.cursor()
    save_sql = """INSERT INTO ipv6_support_degree (domain, server_responds_first_page_delay) VALUES (%s, %f) ON DUPLICATE KEY UPDATE server_responds_first_page_delay = VALUES(server_responds_first_page_delay)"""
    page_ratio = IPv6SupportDegree('www.tsinghua.edu.cn')
    cursor.execute(save_sql, (domain, page_ratio.check_homepage_delay(page_ratio.ipv6delay, page_ratio.ipv4delay)))
    conn.commit()
