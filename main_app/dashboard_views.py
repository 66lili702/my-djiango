# main_app/dashboard_views.py
from django.shortcuts import render
from django.db.models import Avg, Count, Sum, Min, Max
from django.utils import timezone
import json
from .models import LianJiaHouse


def simple_dashboard(request):
    """简单版本的数据大屏 - 不会影响现有功能"""
    # 基础统计
    total_houses = LianJiaHouse.objects.count()
    district_count = LianJiaHouse.objects.values('district').distinct().count()

    # 平均价格
    try:
        avg_price_result = LianJiaHouse.objects.aggregate(avg_price=Avg('unit_price'))
        avg_price = avg_price_result['avg_price']
    except:
        avg_price = 0

    context = {
        'total_houses': total_houses,
        'district_count': district_count,
        'avg_price': round(avg_price, 2) if avg_price else 0,
    }

    return render(request, 'main_app/simple_dashboard.html', context)