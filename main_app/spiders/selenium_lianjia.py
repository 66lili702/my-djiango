from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
import re
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from main_app.models import LianJiaHouse


class SeleniumLianJiaSpider:
    def __init__(self):
        # Chrome选项设置
        self.options = Options()
        self.options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')

        # 初始化浏览器
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # 设置等待时间
        self.wait = WebDriverWait(self.driver, 10)

    def crawl_district(self, district, pages=2):
        """爬取指定区域的数据"""
        print(f"📍 开始爬取 {district} 区域...")

        all_houses = []

        for page in range(1, pages + 1):
            print(f"📄 正在爬取第 {page} 页...")

            url = f"https://bj.lianjia.com/ershoufang/{district}/pg{page}/"
            print(f"🌐 访问: {url}")

            try:
                self.driver.get(url)

                # 等待页面加载
                time.sleep(random.uniform(3, 5))

                # 检查是否有验证码或登录页面
                current_url = self.driver.current_url
                if "verify" in current_url or "login" in current_url or "captcha" in current_url:
                    print("🚫 遇到验证码或登录页面，需要手动处理")
                    input("请手动处理验证码/登录，然后按回车继续...")

                # 等待房源列表加载
                try:
                    self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".sellListContent li, .content__list--item"))
                    )
                except TimeoutException:
                    print("❌ 页面加载超时，未找到房源列表")
                    continue

                # 获取页面源码并解析
                html = self.driver.page_source
                houses = self.parse_page(html, district)
                all_houses.extend(houses)

                print(f"✅ 第 {page} 页获取到 {len(houses)} 个房源")

                # 随机延迟，避免被封
                time.sleep(random.uniform(2, 4))

            except Exception as e:
                print(f"❌ 爬取第 {page} 页失败: {e}")
                continue

        return all_houses

    def parse_page(self, html, district):
        """解析页面内容"""
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, 'html.parser')
        houses = []

        # 查找房源列表
        house_list = soup.select('.sellListContent li, .clear .LOGCLICKDATA, [class*="info clear"]')

        if not house_list:
            print("❌ 未找到房源列表")
            # 保存页面用于调试
            with open(f"selenium_debug_{district}.html", "w", encoding="utf-8") as f:
                f.write(html)
            print(f"💾 调试页面已保存: selenium_debug_{district}.html")
            return houses

        print(f"📊 找到 {len(house_list)} 个房源")

        for i, item in enumerate(house_list):
            try:
                print(f"  解析第 {i + 1} 个房源...")
                house_data = self.parse_house_item(item, district)
                if house_data:
                    houses.append(house_data)
                    print(f"  ✅ 解析成功: {house_data['title'][:20]}...")
            except Exception as e:
                print(f"  ❌ 解析失败: {e}")

        return houses

    def parse_house_item(self, item, district):
        """解析单个房源信息"""
        try:
            # 标题
            title_elem = item.select_one('.title a, .houseInfo a, a[href*="/ershoufang/"]')
            if not title_elem:
                return None

            title = title_elem.get_text(strip=True)
            detail_url = title_elem.get('href', '')
            if detail_url and not detail_url.startswith('http'):
                detail_url = 'https://bj.lianjia.com' + detail_url

            # 总价
            total_price = 0
            price_elem = item.select_one('.totalPrice, .priceInfo .total, .total-price')
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                match = re.search(r'(\d+\.?\d*)', price_text)
                if match:
                    total_price = float(match.group(1))

            # 单价
            unit_price = 0
            unit_price_elem = item.select_one('.unitPrice, .priceInfo .unit, .unit-price')
            if unit_price_elem:
                unit_text = unit_price_elem.get_text(strip=True)
                match = re.search(r'(\d+)', unit_text)
                if match:
                    unit_price = float(match.group(1))

            # 小区
            xiaoqu = '未知'
            position_elem = item.select_one('.positionInfo a, .houseInfo .area a, .communityName a')
            if position_elem:
                xiaoqu = position_elem.get_text(strip=True)

            # 房屋信息
            house_info = ''
            house_info_elem = item.select_one('.houseInfo, .info-col, .house-info')
            if house_info_elem:
                house_info = house_info_elem.get_text(strip=True)

            # 解析详细信息
            layout, area, floor_info, orientation = self.parse_house_info(house_info)

            # 区域映射
            districts = {
                'chaoyang': '朝阳', 'haidian': '海淀', 'dongcheng': '东城',
                'xicheng': '西城', 'fengtai': '丰台', 'shijingshan': '石景山'
            }
            district_cn = districts.get(district, district)

            # 面积
            area_value = 0
            if area and area != '未知':
                match = re.search(r'(\d+\.?\d*)', area)
                if match:
                    area_value = float(match.group(1))

            return {
                'title': title,
                'total_price': total_price,
                'unit_price': unit_price,
                'district': district_cn,
                'area': area_value,
                'layout': layout,
                'xiaoqu': xiaoqu,
                'floor': floor_info,
                'orientation': orientation,
                'description': house_info,
                'source_url': detail_url,
                'city': '北京',
            }

        except Exception as e:
            print(f"解析房源失败: {e}")
            return None

    def parse_house_info(self, house_info):
        """解析房屋信息"""
        layout = area = floor_info = orientation = '未知'
        if house_info:
            parts = [part.strip() for part in house_info.split('|') if part.strip()]
            if len(parts) >= 4:
                layout, area, floor_info, orientation = parts[:4]
        return layout, area, floor_info, orientation

    def save_houses(self, houses):
        """保存数据到数据库"""
        saved_count = 0
        for house_data in houses:
            try:
                # 避免重复
                existing = LianJiaHouse.objects.filter(
                    title=house_data['title'],
                    source_url=house_data['source_url']
                ).exists()

                if not existing:
                    LianJiaHouse.objects.create(**house_data)
                    saved_count += 1
                    print(f"💾 保存: {house_data['title'][:30]}... - {house_data['total_price']}万")
                else:
                    print(f"⏭️ 已存在: {house_data['title'][:30]}...")

            except Exception as e:
                print(f"❌ 保存失败: {e}")

        return saved_count

    def start_crawl(self, max_pages_per_district=2):
        """开始爬虫"""
        print("🚀 开始Selenium爬取链家数据...")
        print("=" * 50)

        count_before = LianJiaHouse.objects.count()
        print(f"📊 爬取前数据库有 {count_before} 条数据")

        districts = {
            'chaoyang': '朝阳',
            'haidian': '海淀',
            'dongcheng': '东城',
            'xicheng': '西城'
        }

        total_saved = 0

        try:
            for district_en, district_cn in districts.items():
                print(f"\n📍 开始爬取 {district_cn} 区域...")

                houses = self.crawl_district(district_en, max_pages_per_district)
                saved_count = self.save_houses(houses)
                total_saved += saved_count

                print(f"📊 {district_cn} 区域: 获取 {len(houses)} 条，新增 {saved_count} 条")

        except Exception as e:
            print(f"❌ 爬取过程出错: {e}")

        finally:
            # 关闭浏览器
            self.driver.quit()
            print("🔚 浏览器已关闭")

        count_after = LianJiaHouse.objects.count()
        print(f"\n" + "=" * 50)
        print(f"🎉 Selenium爬取完成！")
        print(f"📈 新增 {total_saved} 条数据")
        print(f"📊 现在共有 {count_after} 条数据")

        return total_saved