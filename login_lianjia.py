# login_lianjia_fixed.py
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pickle
import os


def login_lianjia():
    """使用Selenium登录链家"""

    try:
        # 配置Chrome选项
        options = webdriver.ChromeOptions()
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])

        # 尝试直接使用Chrome，让Selenium自动管理驱动
        driver = webdriver.Chrome(options=options)

        print("🌐 正在打开浏览器...")

        # 先测试基础连接
        driver.get("https://www.baidu.com")
        print("✅ 浏览器启动成功")

        # 现在访问链家
        driver.get("https://bj.lianjia.com/")
        print("✅ 链家网站访问成功")

        # 点击登录按钮
        try:
            login_btn = driver.find_element(By.LINK_TEXT, "登录")
            login_btn.click()
            print("✅ 点击登录按钮")
            time.sleep(2)
        except:
            # 如果找不到登录按钮，直接访问登录页
            driver.get("https://passport.lianjia.com/login")
            print("✅ 直接访问登录页")

        print("\n⏳ 请在浏览器中完成登录：")
        print("1. 输入手机号/用户名")
        print("2. 输入密码")
        print("3. 完成验证码")
        print("4. 点击登录")
        print("5. 登录成功后，回到这里按回车...")

        input("登录完成后按回车继续...")

        # 获取cookies
        cookies = driver.get_cookies()
        print(f"✅ 获取到 {len(cookies)} 个cookies")

        # 保存cookies
        with open("lianjia_cookies.pkl", "wb") as f:
            pickle.dump(cookies, f)
        print("💾 Cookies已保存")

        # 测试访问房源页面
        driver.get("https://bj.lianjia.com/ershoufang/")
        time.sleep(2)

        if "二手房" in driver.title:
            print("🎉 登录成功！")
            return True
        else:
            print("❌ 可能登录失败")
            return False

    except Exception as e:
        print(f"❌ 出错: {e}")
        return False
    finally:
        try:
            driver.quit()
        except:
            pass


if __name__ == "__main__":
    login_lianjia()