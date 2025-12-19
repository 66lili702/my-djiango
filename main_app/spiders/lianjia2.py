import requests
from bs4 import BeautifulSoup
import time
import random
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from main_app.models import LianJiaHouse


class LianJiaDataGenerator:
    """链家数据生成器"""

    def generate_house_data(self, count=200):
        """生成房源数据"""
        print(f"正在添加 {count} 条房源数据...")

        districts = {
            '朝阳': ['朝阳公园', '国贸', '望京', '三元桥', '大望路', '团结湖', '劲松', '潘家园'],
            '海淀': ['中关村', '五道口', '上地', '苏州街', '万柳', '公主坟', '紫竹桥', '知春路'],
            '东城': ['王府井', '东单', '建国门', '东四', '安定门', '东直门', '和平里', '北新桥'],
            '西城': ['金融街', '西单', '复兴门', '月坛', '德胜门', '西直门', '宣武门', '阜成门'],
            '丰台': ['方庄', '宋家庄', '草桥', '丽泽', '科技园', '刘家窑', '蒲黄榆', '六里桥'],
            '通州': ['梨园', '九棵树', '北苑', '武夷花园', '潞苑'],
            '昌平': ['回龙观', '天通苑', '沙河', '北七家', '霍营']
        }

        layouts = ['1室1厅', '2室1厅', '3室1厅', '3室2厅', '4室2厅']
        orientations = ['南', '北', '南北通透', '东', '西', '东南', '西南', '东北', '西北']

        # 更自然的标题前缀
        title_prefixes = ['', '精装', '豪华', '温馨', '舒适', '简约', '现代', '经典', '优质', '稀缺']
        title_suffixes = ['', '户型方正', '采光好', '交通便利', '配套齐全', '拎包入住', '业主诚心', '急售']

        saved_count = 0

        for i in range(count):
            district = random.choice(list(districts.keys()))
            area = random.choice([60, 70, 80, 90, 100, 110, 120, 130, 150, 180])
            layout = random.choice(layouts)
            xiaoqu = random.choice(districts[district])
            floor_total = random.randint(6, 30)
            floor_current = random.randint(1, floor_total)
            orientation = random.choice(orientations)

            # 随机选择标题修饰词
            prefix = random.choice(title_prefixes)
            suffix = random.choice(title_suffixes)

            # 更自然的价格生成逻辑
            base_prices = {
                '东城': 120000, '西城': 125000,
                '朝阳': 85000, '海淀': 90000,
                '丰台': 60000, '通州': 45000, '昌平': 40000
            }

            base_price = base_prices.get(district, 50000)
            # 价格浮动 ±15%
            price_variation = random.uniform(0.85, 1.15)
            unit_price = int(base_price * price_variation)
            total_price = round((unit_price * area) / 10000, 1)

            # 构建更自然的标题
            if prefix and suffix:
                title = f"{prefix}{xiaoqu}{layout}{area}平{orientation}向{suffix}"
            elif prefix:
                title = f"{prefix}{xiaoqu}{layout}{area}平{orientation}向"
            elif suffix:
                title = f"{xiaoqu}{layout}{area}平{orientation}向{suffix}"
            else:
                title = f"{xiaoqu}{layout}{area}平{orientation}向"

            house_data = {
                'title': title,
                'total_price': total_price,
                'unit_price': unit_price,
                'district': district,
                'area': area,
                'layout': layout,
                'xiaoqu': xiaoqu,
                'floor': f'{floor_current}/{floor_total}',
                'orientation': orientation,
                'description': f'位于{district}区{xiaoqu}，{layout}，建筑面积{area}平米，{orientation}朝向，楼层{floor_current}/{floor_total}，精装修，周边配套完善，交通便利。',
                'source_url': f'https://bj.lianjia.com/ershoufang/10{i:07d}.html',
                'city': '北京',
            }

            try:
                LianJiaHouse.objects.create(**house_data)
                saved_count += 1
                print(f"添加: {title} - {total_price}万")
            except Exception as e:
                print(f"添加失败: {e}")

        print(f"\n数据完成！共 {saved_count} 条数据")
        return saved_count


# 使用方法
def create_sample_data():
    generator = LianJiaDataGenerator()
    return generator.generate_house_data(200)


# 如果要立即生成200条数据，运行：
if __name__ == "__main__":
    create_sample_data()