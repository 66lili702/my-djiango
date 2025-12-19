from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
import time
import csv


def final_lianjia_crawler(city='bj', max_pages=5):
    """最终版链家爬虫 - 一键运行"""

    print(f"🚀 开始爬取 {city} 二手房数据，最多 {max_pages} 页")

    # 浏览器设置
    chrome_options = Options()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')

    service = ChromeService(r'D:\Users\lenovo\PycharmProjects\djiango毕设\chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        filename = f'final_{city}_houses.csv'
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(
                ['标题', '总价(万)', '单价(元/平)', '户型', '面积(平)', '朝向', '装修', '楼层', '年份', '小区', '区域',
                 '链接'])

            total_houses = 0

            for page in range(1, max_pages + 1):
                print(f"\n📄 第 {page}/{max_pages} 页...")

                # 访问页面
                if page == 1:
                    url = f'https://{city}.lianjia.com/ershoufang/'
                else:
                    url = f'https://{city}.lianjia.com/ershoufang/pg{page}/'

                driver.get(url)
                time.sleep(3)

                # 获取房屋列表
                houses = driver.find_elements(By.CSS_SELECTOR, '.sellListContent li')
                print(f"找到 {len(houses)} 个房屋")

                if len(houses) == 0:
                    print("⚠️  没有数据，停止爬取")
                    break

                page_count = 0
                for house in houses:
                    house_data = safe_extract(house)
                    if house_data and house_data['title']:  # 确保有标题
                        writer.writerow([
                            house_data['title'],
                            house_data.get('total_price', ''),
                            house_data.get('unit_price', ''),
                            house_data.get('layout', ''),
                            house_data.get('area', ''),
                            house_data.get('direction', ''),
                            house_data.get('decoration', ''),
                            house_data.get('floor', ''),
                            house_data.get('year', ''),
                            house_data.get('community', ''),
                            house_data.get('district', ''),
                            house_data.get('link', '')
                        ])
                        page_count += 1
                        total_houses += 1

                print(f"✅ 第{page}页提取 {page_count} 个房屋")

                if page_count == 0:
                    print("⚠️  本页没有提取到数据，停止爬取")
                    break

                time.sleep(1)  # 礼貌延迟

        print(f"\n🎉 完成！共提取 {total_houses} 个房屋")
        print(f"📁 数据保存到: {filename}")

    except Exception as e:
        print(f"❌ 错误: {e}")
    finally:
        driver.quit()


def safe_extract(house_element):
    """安全提取数据"""
    data = {}

    # 标题和链接
    try:
        title_elem = house_element.find_element(By.CSS_SELECTOR, '.title a')
        data['title'] = title_elem.text
        data['link'] = title_elem.get_attribute('href')
    except:
        return None

    # 价格
    try:
        price_elem = house_element.find_element(By.CSS_SELECTOR, '.totalPrice span')
        data['total_price'] = price_elem.text
    except:
        data['total_price'] = ''

    # 单价
    try:
        unit_price_elem = house_element.find_element(By.CSS_SELECTOR, '.unitPrice')
        data['unit_price'] = unit_price_elem.text
    except:
        data['unit_price'] = ''

    # 房屋信息
    try:
        info_elem = house_element.find_element(By.CSS_SELECTOR, '.houseInfo')
        info_parts = info_elem.text.split('|')
        data['layout'] = info_parts[0].strip() if len(info_parts) > 0 else ""
        data['area'] = info_parts[1].strip() if len(info_parts) > 1 else ""
        data['direction'] = info_parts[2].strip() if len(info_parts) > 2 else ""
        data['decoration'] = info_parts[3].strip() if len(info_parts) > 3 else ""
        data['floor'] = info_parts[4].strip() if len(info_parts) > 4 else ""
        data['year'] = info_parts[5].strip() if len(info_parts) > 5 else ""
    except:
        pass

    # 位置信息
    try:
        pos_elem = house_element.find_element(By.CSS_SELECTOR, '.positionInfo')
        pos_parts = pos_elem.text.split('-')
        data['community'] = pos_parts[0].strip() if len(pos_parts) > 0 else ""
        data['district'] = pos_parts[1].strip() if len(pos_parts) > 1 else ""
    except:
        pass

    return data


# 🎯 一键运行！
if __name__ == "__main__":
    # 你可以修改这些参数
    city = 'bj'  # 城市: bj-北京, sh-上海, gz-广州, sz-深圳
    pages = 3  # 爬取页数

    final_lianjia_crawler(city=city, max_pages=pages)