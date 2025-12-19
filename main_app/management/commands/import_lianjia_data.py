import os
import django
import random
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from main_app.models import LianJiaHouse


class Command(BaseCommand):
    help = '导入链家房源数据到数据库'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=200, help='要生成的数据数量')

    def handle(self, *args, **options):
        count = options['count']
        self.import_complete_data(count)

    def import_complete_data(self, count=200):
        """完整字段数据导入"""

        districts = {
            '朝阳': ['朝阳公园', '国贸', '望京', '三元桥', '大望路', '团结湖', '劲松', 'CBD'],
            '海淀': ['中关村', '五道口', '上地', '苏州街', '万柳', '公主坟', '学院路'],
            '东城': ['王府井', '东单', '建国门', '东四', '安定门', '东直门'],
            '西城': ['金融街', '西单', '复兴门', '月坛', '德胜门', '阜成门'],
            '丰台': ['方庄', '宋家庄', '草桥', '丽泽', '科技园'],
        }

        layouts = ['1室1厅', '2室1厅', '3室1厅', '3室2厅', '4室2厅', '4室1厅']
        orientations = ['南', '北', '东', '西', '东南', '西南', '东北', '西北', '南北通透']

        created_count = 0

        for i in range(count):
            # 随机生成数据
            district = random.choice(list(districts.keys()))
            xiaoqu = random.choice(districts[district])
            layout = random.choice(layouts)
            area_size = random.choice([60.0, 70.0, 80.0, 90.0, 100.0, 110.0, 120.0, 130.0, 150.0, 180.0])
            orientation = random.choice(orientations)

            # 楼层信息
            floor_total = random.randint(6, 30)
            floor_current = random.randint(1, floor_total)
            floor_info = f"{floor_current}/{floor_total}"

            # 生成合理的价格
            if district in ['东城', '西城']:
                unit_price = random.randint(80000, 150000)
            elif district in ['朝阳', '海淀']:
                unit_price = random.randint(60000, 100000)
            else:
                unit_price = random.randint(40000, 70000)

            total_price = round((unit_price * area_size) / 10000, 1)

            # 生成随机爬取时间（最近30天内）
            random_days = random.randint(0, 30)
            random_hours = random.randint(0, 23)
            random_minutes = random.randint(0, 59)
            crawl_time = timezone.now() - timedelta(
                days=random_days,
                hours=random_hours,
                minutes=random_minutes
            )

            # 创建房源标题和描述
            title = f"{xiaoqu} {layout} {area_size}平米"
            description = f"位于{district}区{xiaoqu}，{layout}，建筑面积{area_size}平米，{orientation}朝向，楼层{floor_info}，精装修，周边配套完善，交通便利。"

            # 图片URL（模拟）
            pic_url = f"https://example.com/house_{i % 10 + 1}.jpg"

            # 源URL
            source_url = f"https://bj.lianjia.com/ershoufang/10{i:07d}.html"

            try:
                # 使用所有字段创建对象
                house = LianJiaHouse(
                    title=title,
                    total_price=total_price,
                    unit_price=float(unit_price),
                    district=district,
                    area=area_size,
                    layout=layout,
                    xiaoqu=xiaoqu,
                    floor=floor_info,
                    orientation=orientation,
                    description=description,
                    pic_url=pic_url,
                    crawl_time=crawl_time,
                    source_url=source_url,
                    city='北京'
                )
                house.save()
                created_count += 1
                print(f"✅ 已创建: {title} - {total_price}万 - {district}")
            except Exception as e:
                print(f"❌ 创建失败: {e}")

        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 成功导入 {created_count} 条房源数据到数据库！')
        )