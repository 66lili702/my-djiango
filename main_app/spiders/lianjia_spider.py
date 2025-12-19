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


class LianJiaSpider:
    def __init__(self):
        self.base_url = "https://bj.lianjia.com/ershoufang/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Cache-Control': 'max-age=0',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        # 设置登录后的Cookie
        self.set_login_cookies()

    # def set_login_cookies(self):
    #     """设置登录后的完整Cookie"""
    #     # 在这里粘贴你从浏览器复制的完整Cookie字符串
    #     cookie_str = "lianjia_uuid=9394be92-e311-428f-a118-762c0fef6ddc; _jzqy=1.1758703393.1758703393.1.jzqsr=baidu|jzqct=%E9%93%BE%E5%AE%B6%E5%9C%B0%E4%BA%A7%E4%BA%8C%E6%89%8B%E6%88%BF%E7%BD%91.-; _ga=GA1.2.1351789322.1758704949; _ga_RCTBRFLNVS=GS2.2.s1758704949$o1$g0$t1758704949$j60$l0$h0; crosSdkDT2019DeviceId=-3r0b1t--8v9oce-o8j31oq76kveydb-lt7hfrso7; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221997ae4185c53f-00138ca767c7128-26061951-1327104-1997ae4185d1826%22%2C%22%24device_id%22%3A%221997ae4185c53f-00138ca767c7128-26061951-1327104-1997ae4185d1826%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_utm_source%22%3A%22baidu%22%2C%22%24latest_utm_medium%22%3A%22pinzhuan%22%2C%22%24latest_utm_campaign%22%3A%22wybj%22%2C%22%24latest_utm_content%22%3A%22biaotimiaoshu%22%2C%22%24latest_utm_term%22%3A%22biaoti%22%7D%7D; Hm_lvt_46bf127ac9b856df503ec2dbf942b67e=1762336612,1763694620; HMACCOUNT=B7D1389E40F3F226; _jzqc=1; _qzjc=1; lianjia_ssid=cc993f3a-53bd-41ca-be39-e98472354aea; select_city=110000; _jzqa=1.2032640898777823200.1758703393.1763694620.1763953258.5; _jzqx=1.1759040005.1763953258.2.jzqsr=bj%2Elianjia%2Ecom|jzqct=/ershoufang/.jzqsr=bj%2Elianjia%2Ecom|jzqct=/; _jzqckmp=1; _gid=GA1.2.1380707053.1763953270; login_ucid=2000000513867274; lianjia_token=2.00117ae97e4a417a9800d7c04fe36cc461; lianjia_token_secure=2.00117ae97e4a417a9800d7c04fe36cc461; security_ticket=DqAgTo35q5EnvulIl6MwH+2PPNurOZL406zYgK3rxpy0/wWF3wEDR1cBZkCkVBQ3YGG+QtX2b6A4VuzAoXn5JiI/LfXqooRlTN7QOfM6TcAiJATdiL6AT1tx3i8qXx0l25xG+5w8MRvCb6oWMSsI22p8ZfZy4fJGUKaTV7Vbz8A=; ftkrc_=7f2e02be-1e05-4399-a6bd-99b77b64515e; lfrc_=1b0e9ba5-8fd4-4922-9a84-2ad2b2a1ca64; _qzja=1.997919910.1758703393575.1763694620105.1763953258428.1763954439704.1763954493584.0.0.0.14.5; _qzjb=1.1763953258428.5.0.0.0; _qzjto=5.1.0; _jzqb=1.5.10.1763953258.1; Hm_lpvt_46bf127ac9b856df503ec2dbf942b67e=1763954494; srcid=eyJ0Ijoie1wiZGF0YVwiOlwiZTYzZmMyNTA3NWE4ZWZjNjI2OTFjZTk0OTJmZmRiZDJjOWUxNjY5ZTc3ODllYTJhN2M2ZDgyOGNhOGU5ZmRlYmI5Y2NiODNlNTMwYWExNTQ3ZTU0NDMxZjU2ZTNlYjAwMzFjZjQ2MGMzYWYyYzEwM2I1NTQzNjEzYmNmMGExN2FjYzA0NmY2MGE0N2YzZWUwYzhhM2E4ZjhkZmRmNzYxNjc5OGM0YjI2MDI5ODQyZTM4ZWVmYjFhYzZiNWQ0ZGJjMWI1OGE3N2M0NGEyMzgyZGJmZmQ5NjU0NWNkMjA3NTc2ZDc4ZWEzYjUxYWIzMTRkMTQ3NWViMjRhOWJkMGE5MlwiLFwia2V5X2lkXCI6XCIxXCIsXCJzaWduXCI6XCI1ZDU2OTQwZVwifSIsInIiOiJodHRwczovL2JqLmxpYW5qaWEuY29tLyIsIm9zIjoid2ViIiwidiI6IjAuMSJ9; _ga_KJTRWRHDL1=GS2.2.s1763953270$o4$g1$t1763954504$j8$l0$h0; _ga_QJN1VP0CMS=GS2.2.s1763953270$o4$g1$t1763954504$j8$l0$h0"
    #     self.session.headers.update(self.headers)
    #     print("✅ Cookie已更新为登录状态")
    def set_login_cookies(self):
        """设置登录后的完整Cookie"""
        # 在这里粘贴你从浏览器复制的完整Cookie字符串
        cookie_str = "lianjia_uuid=9394be92-e311-428f-a118-762c0fef6ddc; _jzqy=1.1758703393.1758703393.1.jzqsr=baidu|jzqct=%E9%93%BE%E5%AE%B6%E5%9C%B0%E4%BA%A7%E4%BA%8C%E6%89%8B%E6%88%BF%E7%BD%91.-; _ga=GA1.2.1351789322.1758704949; _ga_RCTBRFLNVS=GS2.2.s1758704949$o1$g0$t1758704949$j60$l0$h0; crosSdkDT2019DeviceId=-3r0b1t--8v9oce-o8j31oq76kveydb-lt7hfrso7; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221997ae4185c53f-00138ca767c7128-26061951-1327104-1997ae4185d1826%22%2C%22%24device_id%22%3A%221997ae4185c53f-00138ca767c7128-26061951-1327104-1997ae4185d1826%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_utm_source%22%3A%22baidu%22%2C%22%24latest_utm_medium%22%3A%22pinzhuan%22%2C%22%24latest_utm_campaign%22%3A%22wybj%22%2C%22%24latest_utm_content%22%3A%22biaotimiaoshu%22%2C%22%24latest_utm_term%22%3A%22biaoti%22%7D%7D; Hm_lvt_46bf127ac9b856df503ec2dbf942b67e=1762336612,1763694620; HMACCOUNT=B7D1389E40F3F226; _jzqc=1; _qzjc=1; lianjia_ssid=cc993f3a-53bd-41ca-be39-e98472354aea; select_city=110000; _jzqa=1.2032640898777823200.1758703393.1763694620.1763953258.5; _jzqx=1.1759040005.1763953258.2.jzqsr=bj%2Elianjia%2Ecom|jzqct=/ershoufang/.jzqsr=bj%2Elianjia%2Ecom|jzqct=/; _jzqckmp=1; _gid=GA1.2.1380707053.1763953270; login_ucid=2000000513867274; lianjia_token=2.00117ae97e4a417a9800d7c04fe36cc461; lianjia_token_secure=2.00117ae97e4a417a9800d7c04fe36cc461; security_ticket=DqAgTo35q5EnvulIl6MwH+2PPNurOZL406zYgK3rxpy0/wWF3wEDR1cBZkCkVBQ3YGG+QtX2b6A4VuzAoXn5JiI/LfXqooRlTN7QOfM6TcAiJATdiL6AT1tx3i8qXx0l25xG+5w8MRvCb6oWMSsI22p8ZfZy4fJGUKaTV7Vbz8A=; ftkrc_=7f2e02be-1e05-4399-a6bd-99b77b64515e; lfrc_=1b0e9ba5-8fd4-4922-9a84-2ad2b2a1ca64; _qzja=1.997919910.1758703393575.1763694620105.1763953258428.1763954439704.1763954493584.0.0.0.14.5; _qzjb=1.1763953258428.5.0.0.0; _qzjto=5.1.0; _jzqb=1.5.10.1763953258.1; Hm_lpvt_46bf127ac9b856df503ec2dbf942b67e=1763954494; srcid=eyJ0Ijoie1wiZGF0YVwiOlwiZTYzZmMyNTA3NWE4ZWZjNjI2OTFjZTk0OTJmZmRiZDJjOWUxNjY5ZTc3ODllYTJhN2M2ZDgyOGNhOGU5ZmRlYmI5Y2NiODNlNTMwYWExNTQ3ZTU0NDMxZjU2ZTNlYjAwMzFjZjQ2MGMzYWYyYzEwM2I1NTQzNjEzYmNmMGExN2FjYzA0NmY2MGE0N2YzZWUwYzhhM2E4ZjhkZmRmNzYxNjc5OGM0YjI2MDI5ODQyZTM4ZWVmYjFhYzZiNWQ0ZGJjMWI1OGE3N2M0NGEyMzgyZGJmZmQ5NjU0NWNkMjA3NTc2ZDc4ZWEzYjUxYWIzMTRkMTQ3NWViMjRhOWJkMGE5MlwiLFwia2V5X2lkXCI6XCIxXCIsXCJzaWduXCI6XCI1ZDU2OTQwZVwifSIsInIiOiJodHRwczovL2JqLmxpYW5qaWEuY29tLyIsIm9zIjoid2ViIiwidiI6IjAuMSJ9; _ga_KJTRWRHDL1=GS2.2.s1763953270$o4$g1$t1763954504$j8$l0$h0; _ga_QJN1VP0CMS=GS2.2.s1763953270$o4$g1$t1763954504$j8$l0$h0"

        # 正确的方法：直接更新headers中的Cookie，然后更新session
        self.headers['Cookie'] = cookie_str
        self.session.headers.update(self.headers)

        print("✅ Cookie已更新为登录状态")

    def get_districts(self):
        """获取区域列表"""
        return {
            'chaoyang': '朝阳',
            'haidian': '海淀',
            'dongcheng': '东城',
            'xicheng': '西城',
            'fengtai': '丰台',
            'shijingshan': '石景山',
            'tongzhou': '通州',
            'changping': '昌平',
            'daxing': '大兴'
        }

    def get_page_data(self, district, page):
        """获取页面数据"""
        url = f"{self.base_url}{district}/pg{page}/"
        print(f"🌐 正在爬取: {url}")

        try:
            # 随机延迟，避免被封
            time.sleep(random.uniform(3, 6))

            response = self.session.get(url, timeout=15)

            if response.status_code == 200:
                # 检查是否被反爬
                if "验证" in response.text or "antispider" in response.text:
                    print("🚫 触发反爬机制")
                    return []

                return self.parse_page(response.text, district)
            else:
                print(f"❌ 请求失败，状态码: {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return []

    def parse_page(self, html, district):
        """解析页面"""
        soup = BeautifulSoup(html, 'html.parser')
        houses = []

        # 尝试多种选择器
        selectors = [
            '.sellListContent li',
            '.sellListContent > li',
            'li.clear',
            '.clear.LOGCLICKDATA',
            '.content__list--item',
            '[class*="info clear"]'
        ]

        house_list = None
        for selector in selectors:
            house_list = soup.select(selector)
            if house_list:
                print(f"✅ 使用选择器: {selector}")
                break

        if not house_list:
            print("❌ 未找到房源列表")
            # 保存页面用于调试
            with open(f"debug_{district}.html", "w", encoding="utf-8") as f:
                f.write(html)
            print(f"💾 调试页面已保存: debug_{district}.html")
            return houses

        print(f"📊 找到 {len(house_list)} 个房源")

        for item in house_list:
            house_data = self.parse_house_item(item, district)
            if house_data:
                houses.append(house_data)

        return houses

    def parse_house_item(self, item, district):
        """解析单个房源"""
        try:
            # 标题
            title_elem = item.select_one('.title a')
            if not title_elem:
                return None

            title = title_elem.text.strip()
            detail_url = title_elem.get('href', '')
            if detail_url and not detail_url.startswith('http'):
                detail_url = 'https://bj.lianjia.com' + detail_url

            # 总价
            total_price = 0
            price_elem = item.select_one('.totalPrice')
            if price_elem:
                price_text = price_elem.text.strip()
                match = re.search(r'(\d+\.?\d*)', price_text)
                if match:
                    total_price = float(match.group(1))

            # 单价
            unit_price = 0
            unit_price_elem = item.select_one('.unitPrice')
            if unit_price_elem:
                unit_text = unit_price_elem.text.strip()
                match = re.search(r'(\d+)', unit_text)
                if match:
                    unit_price = float(match.group(1))

            # 小区
            xiaoqu = '未知'
            xiaoqu_elem = item.select_one('.positionInfo a')
            if xiaoqu_elem:
                xiaoqu = xiaoqu_elem.text.strip()

            # 房屋信息
            house_info = ''
            house_info_elem = item.select_one('.houseInfo')
            if house_info_elem:
                house_info = house_info_elem.text.strip()

            # 解析详细信息
            layout, area, floor_info, orientation = self.parse_house_info(house_info)

            # 区域
            districts = self.get_districts()
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
        """保存数据"""
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
                    print(f"✅ 保存: {house_data['title'][:30]}... - {house_data['total_price']}万")
                else:
                    print(f"⏭️ 已存在: {house_data['title'][:30]}...")

            except Exception as e:
                print(f"❌ 保存失败: {e}")

        return saved_count

    def start_crawl(self, max_pages_per_district=5):
        """开始爬虫"""
        print("🚀 开始大规模爬取链家数据...")
        print("=" * 50)

        count_before = LianJiaHouse.objects.count()
        print(f"📊 爬取前数据库有 {count_before} 条数据")

        districts = self.get_districts()
        total_saved = 0

        for district_en, district_cn in districts.items():
            print(f"\n📍 开始爬取 {district_cn} 区域...")

            for page in range(1, max_pages_per_district + 1):
                print(f"📄 正在爬取第 {page} 页...")
                houses = self.get_page_data(district_en, page)

                if not houses:
                    print(f"💤 第 {page} 页没有数据，休息后继续...")
                    time.sleep(5)
                    continue

                saved_count = self.save_houses(houses)
                total_saved += saved_count

                print(f"📊 {district_cn} 第 {page} 页: 获取 {len(houses)} 条，新增 {saved_count} 条")

                # 页面间延迟
                time.sleep(random.uniform(2, 4))

        count_after = LianJiaHouse.objects.count()
        print(f"\n" + "=" * 50)
        print(f"🎉 爬取完成！")
        print(f"📈 新增 {total_saved} 条数据")
        print(f"📊 现在共有 {count_after} 条数据")

        return total_saved