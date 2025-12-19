import requests
from bs4 import BeautifulSoup
import time
import random
import re
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from main_app.models import LianJiaHouse


class LianJiaBypassSpider:
    def __init__(self):
        self.base_url = "https://bj.lianjia.com/ershoufang/"
        self.session = requests.Session()

        # 设置非常真实的请求头
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://bj.lianjia.com/',
        }

    def get_districts(self):
        return {
            'chaoyang': '朝阳',
            'haidian': '海淀',
            'dongcheng': '东城',
            'xicheng': '西城'
        }

    def get_page_with_proxy(self, url, max_retries=3):
        """使用代理和重试机制获取页面"""
        for attempt in range(max_retries):
            try:
                # 每次请求前随机延迟
                delay = random.uniform(5, 15)
                print(f"⏰ 延迟 {delay:.1f}秒后请求...")
                time.sleep(delay)

                # 模拟人类行为：先访问首页
                if attempt == 0:
                    self.session.get("https://bj.lianjia.com/", timeout=10)
                    time.sleep(2)

                response = self.session.get(url, timeout=15)

                if response.status_code == 200:
                    # 检查是否是真实页面
                    if "sellListContent" in response.text:
                        print("✅ 成功获取房源页面")
                        return response
                    elif "验证" in response.text or "login" in response.text:
                        print(f"🚫 第{attempt + 1}次尝试被反爬")
                        continue
                    else:
                        print("⚠️ 页面结构异常")
                else:
                    print(f"❌ 请求失败: {response.status_code}")

            except Exception as e:
                print(f"❌ 请求异常: {e}")

            # 重试前等待更长时间
            time.sleep(10 * (attempt + 1))

        return None

    def parse_page_smart(self, html, district):
        """智能解析页面，自动适应不同结构"""
        soup = BeautifulSoup(html, 'html.parser')
        houses = []

        # 多种可能的房源容器选择器
        container_selectors = [
            '.sellListContent',
            '.content__list',
            '.house-lst',
            '.ershoufang-list',
            '[class*="list-content"]'
        ]

        # 多种房源项选择器
        item_selectors = [
            'li',
            '.item',
            '.list-item',
            '[class*="info"]'
        ]

        for container_selector in container_selectors:
            container = soup.select_one(container_selector)
            if container:
                print(f"✅ 找到容器: {container_selector}")

                for item_selector in item_selectors:
                    items = container.select(item_selector)
                    if items:
                        print(f"✅ 使用选择器: {container_selector} {item_selector}, 找到 {len(items)} 个元素")

                        for item in items:
                            house_data = self.parse_house_item_smart(item, district)
                            if house_data:
                                houses.append(house_data)
                        break
                break

        if not houses:
            print("❌ 未找到任何房源数据")
            # 保存页面用于分析
            with open(f"analysis_{district}.html", "w", encoding="utf-8") as f:
                f.write(html)
            print(f"💾 分析页面已保存: analysis_{district}.html")

        return houses

    def parse_house_item_smart(self, item, district):
        """智能解析房源项"""
        try:
            # 尝试多种标题选择器
            title = None
            detail_url = None

            # 查找包含"ershoufang"的链接
            links = item.find_all('a', href=re.compile(r'ershoufang'))
            for link in links:
                if link.text.strip():
                    title = link.text.strip()
                    detail_url = link.get('href', '')
                    if detail_url and not detail_url.startswith('http'):
                        detail_url = 'https://bj.lianjia.com' + detail_url
                    break

            if not title:
                return None

            # 查找价格信息
            price_text = item.get_text()
            total_price = 0
            price_match = re.search(r'(\d+\.?\d*)\s*万', price_text)
            if price_match:
                total_price = float(price_match.group(1))

            # 查找单价
            unit_price = 0
            unit_match = re.search(r'单价(\d+)', price_text)
            if unit_match:
                unit_price = float(unit_match.group(1))

            # 区域
            districts = self.get_districts()
            district_cn = districts.get(district, district)

            return {
                'title': title,
                'total_price': total_price,
                'unit_price': unit_price,
                'district': district_cn,
                'area': 0,  # 简化处理
                'layout': '未知',
                'xiaoqu': '未知',
                'floor': '未知',
                'orientation': '未知',
                'description': title,
                'source_url': detail_url,
                'city': '北京',
            }

        except Exception as e:
            print(f"解析房源失败: {e}")
            return None

    def save_houses(self, houses):
        """保存数据"""
        saved_count = 0
        for house_data in houses:
            try:
                existing = LianJiaHouse.objects.filter(
                    title=house_data['title'],
                    source_url=house_data['source_url']
                ).exists()

                if not existing:
                    LianJiaHouse.objects.create(**house_data)
                    saved_count += 1
                    print(f"✅ 保存: {house_data['title'][:30]}... - {house_data['total_price']}万")
            except Exception as e:
                print(f"❌ 保存失败: {e}")

        return saved_count

    def start_crawl(self, max_pages_per_district=2):
        """开始爬虫"""
        print("🚀 开始绕过反爬爬取链家数据...")

        districts = self.get_districts()
        total_saved = 0

        for district_en, district_cn in districts.items():
            print(f"\n📍 开始爬取 {district_cn} 区域...")

            for page in range(1, max_pages_per_district + 1):
                url = f"{self.base_url}{district_en}/pg{page}/"
                print(f"📄 正在爬取第 {page} 页: {url}")

                response = self.get_page_with_proxy(url)
                if not response:
                    print(f"❌ 跳过 {district_cn} 第 {page} 页")
                    continue

                houses = self.parse_page_smart(response.text, district_en)
                saved_count = self.save_houses(houses)
                total_saved += saved_count

                print(f"📊 {district_cn} 第 {page} 页: 获取 {len(houses)} 条，新增 {saved_count} 条")

        print(f"\n🎉 绕过爬取完成！新增 {total_saved} 条数据")
        return total_saved