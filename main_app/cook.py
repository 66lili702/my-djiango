from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
import time
import pickle
import os

# 使用链家网站的IP地址直接访问（绕过DNS解析）
# 先获取链家网站的实际IP
import socket

try:
    # 获取链家域名的IP地址
    ip = socket.gethostbyname('www.lianjia.com')
    print(f"链家网站IP地址: {ip}")

    # 使用IP访问
    chromedriver_path = r'D:\Users\lenovo\PycharmProjects\djiango毕设\chromedriver.exe'
    service = ChromeService(chromedriver_path)
    driver = webdriver.Chrome(service=service)

    # 使用IP地址访问
    driver.get(f'http://{ip}')
    print("✅ 使用IP访问成功！")
    time.sleep(3)

    # 现在再尝试用域名访问
    driver.get('https://www.lianjia.com')
    print("✅ 域名访问也成功了！")

except Exception as e:
    print(f"❌ 错误: {e}")