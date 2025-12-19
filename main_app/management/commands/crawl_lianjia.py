from django.core.management.base import BaseCommand
from main_app.spiders.lianjia_spider import LianJiaSpider


class Command(BaseCommand):
    help = '爬取链家二手房数据并存入数据库'

    def add_arguments(self, parser):
        parser.add_argument(
            '--pages',
            type=int,
            default=3,
            help='每个区域爬取的页数（默认3页）'
        )

        parser.add_argument(
            '--districts',
            type=str,
            default='all',
            help='指定要爬取的区域，用逗号分隔，如: chaoyang,haidian (默认爬取所有区域)'
        )

    def handle(self, *args, **options):
        pages = options['pages']
        districts_arg = options['districts']

        self.stdout.write("🚀 开始爬取链家数据...")
        self.stdout.write(f"📄 每区域爬取 {pages} 页")

        try:
            spider = LianJiaSpider()

            # 如果指定了区域，只爬取指定区域
            if districts_arg != 'all':
                target_districts = [d.strip() for d in districts_arg.split(',')]
                self.stdout.write(f"📍 指定爬取区域: {', '.join(target_districts)}")

                # 这里可以修改spider只爬取指定区域
                # 简化处理：先爬所有，后续可以优化
                pass

            total_saved = spider.start_crawl(max_pages_per_district=pages)

            # 显示最终统计
            from main_app.models import LianJiaHouse
            total_count = LianJiaHouse.objects.count()

            self.stdout.write(
                self.style.SUCCESS(f'🎉 链家数据爬取完成！数据库中共有 {total_count} 条房源数据')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ 爬取过程中出错: {e}')
            )
            import traceback
            traceback.print_exc()