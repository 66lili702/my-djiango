import requests
import json
import time
import random
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from main_app.models import LianJiaHouse


class LianJiaMobileSpider:
    def __init__(self):
        self.api_url = "https://app.api.lianjia.com/house/ershoufang/searchv2"
        self.headers = {
            'User-Agent': 'Lianjia/9.23.0 (com.lianjia.beike; build:923010; iOS 14.0.0) Alamofire/4.8.2',
            'Accept': '*/*',
            'Accept-Language': 'zh-Hans-CN;q=1.0',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Lianjia-Channel': 'AppStore',
            'Lianjia-Device-Id': '你的设备ID',
            'Lianjia-Version': '9.23.0',
            'Lianjia-City-Id': '110000',  # 北京
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_districts(self):
        """获取区域代码"""
        return {
            'chaoyang': '朝阳',
            'haidian': '海淀',
            'dongcheng': '东城',
            'xicheng': '西城',
            'fengtai': '丰台',
            'shijingshan': '石景山'
        }

    def get_district_code(self, district_en):
        """获取区域代码"""
        district_codes = {
            'chaoyang': '朝阳',
            'haidian': '海淀',
            'dongcheng': '东城',
            'xicheng': '西城',
            'fengtai': '丰台',
            'shijingshan': '石景山'
        }
        # 这里需要实际的区域代码，可以先测试用朝阳区
        return '511100747'  # 朝阳区代码

    def get_api_data(self, district, page, limit=30):
        """通过API获取数据"""
        params = {
            'city_id': '110000',
            'limit': limit,
            'offset': (page - 1) * limit,
            'condition': f'{district}/',
            'request_ts': int(time.time()),
            'source': 'app',
        }

        try:
            print(f"📡 API请求: {district} 第{page}页")
            response = self.session.get(self.api_url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    return data.get('data', {}).get('list', [])
                else:
                    print(f"❌ API返回错误: {data.get('message')}")
            else:
                print(f"❌ API请求失败: {response.status_code}")

        except Exception as e:
            print(f"❌ API请求异常: {e}")

        return []

    def parse_house_data(self, house_json, district):
        """解析API返回的房源数据"""
        try:
            title = house_json.get('title', '')
            total_price = house_json.get('price', 0)
            unit_price = house_json.get('unit_price', 0)
            area = house_json.get('area', 0)
            layout = house_json.get('layout', '')
            xiaoqu = house_json.get('resblock_name', '')
            floor_info = f"{house_json.get('floor_state', '')}/{house_json.get('total_floor', '')}"
            orientation = house_json.get('orientation', '')

            # 构建详情页URL
            house_code = house_json.get('house_code', '')
            detail_url = f"https://m.lianjia.com/bj/ershoufang/{house_code}.html" if house_code else ''

            districts = self.get_districts()
            district_cn = districts.get(district, district)

            return {
                'title': title,
                'total_price': total_price,
                'unit_price': unit_price,
                'district': district_cn,
                'area': area,
                'layout': layout,
                'xiaoqu': xiaoqu,
                'floor': floor_info,
                'orientation': orientation,
                'description': title,
                'source_url': detail_url,
                'city': '北京',
            }
        except Exception as e:
            print(f"解析API数据失败: {e}")
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
                    print(f"✅ 保存: {house_data['title'][:20]}... - {house_data['total_price']}万")
            except Exception as e:
                print(f"❌ 保存失败: {e}")

        return saved_count

    def start_crawl(self, max_pages_per_district=3):
        """开始爬虫"""
        print("🚀 开始通过移动端API爬取链家数据...")

        districts = self.get_districts()
        total_saved = 0

        for district_en, district_cn in districts.items():
            print(f"\n📍 开始爬取 {district_cn} 区域...")

            for page in range(1, max_pages_per_district + 1):
                print(f"📄 正在爬取第 {page} 页...")

                houses_data = self.get_api_data(district_en, page)
                if not houses_data:
                    print(f"💤 第 {page} 页没有数据")
                    continue

                houses = []
                for house_json in houses_data:
                    house = self.parse_house_data(house_json, district_en)
                    if house:
                        houses.append(house)

                saved_count = self.save_houses(houses)
                total_saved += saved_count

                print(f"📊 {district_cn} 第 {page} 页: 获取 {len(houses)} 条，新增 {saved_count} 条")

                time.sleep(random.uniform(2, 4))

        print(f"\n🎉 API爬取完成！新增 {total_saved} 条数据")
        return total_saved