from django.contrib import admin
from .models import LianJiaHouse


@admin.register(LianJiaHouse)
class LianJiaHouseAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'total_price', 'unit_price', 'district', 'area', 'layout', 'city', 'crawl_time']
    list_display_links = ['id', 'title']

    # 添加城市筛选
    list_filter = ['city', 'district', 'crawl_time']

    search_fields = ['title', 'district', 'xiaoqu']
    list_per_page = 50  # 增加每页显示数量

    # 添加日期层次导航
    date_hierarchy = 'crawl_time'

    # 添加一些管理动作
    actions = ['calculate_avg_price']

    def calculate_avg_price(self, request, queryset):
        from django.db.models import Avg
        avg_price = queryset.aggregate(avg=Avg('unit_price'))['avg']
        self.message_user(request, f'选中房源的均价为: {avg_price:.2f} 元/平米')

    calculate_avg_price.short_description = '计算选中房源均价'