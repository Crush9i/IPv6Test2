from selenium import webdriver
from PIL import Image
import numpy as np
import time
import cv2
from skimage.metrics import structural_similarity as compare_ssim


# # 初始化IPv4和IPv6信息收集对象
# ipv4_info = InformationIPv4("https://www.baidu.com")
# ipv6_info = InformationIPv6("https://www.baidu.com")
#
# # 使用Chrome浏览器，需安装对应的Chrome WebDriver
# driver = webdriver.Chrome()
#
# # 访问IPv4网站并截图
# ipv4_url = "https://www.baidu.com"
# driver.get(ipv4_url)
# driver.save_screenshot("ipv4_screenshot.png")
#
#
# # 访问IPv6网站并截图
# ipv6_url = "https://www.baidu.com"
# driver.get(ipv6_url)
# driver.save_screenshot("ipv6_screenshot.png")
#
# # 关闭浏览器
# driver.quit()
#
# # 加载截图并显示
# ipv4_screenshot = Image.open("ipv4_screenshot.png")
#
# #ipv4_screenshot.show()
# ipv6_screenshot = Image.open("ipv6_screenshot.png")
# #ipv6_screenshot.show()


def image_similarity(ipv4_img, ipv6_img):
    # 读取两张图片
    image1 = cv2.imread(ipv4_img)
    image2 = cv2.imread(ipv6_img)

    # 将图片转换为灰度
    gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

    # 计算两张图片的结构相似度指数（SSIM）
    (score, diff) = compare_ssim(gray1, gray2, full=True)
    similarity = int(score * 100)
    # 输出相似度百分比
    print(f"图片相似度为: {similarity}%")
    return similarity




