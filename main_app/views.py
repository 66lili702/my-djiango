# main_app/views.py
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Sum, Min, Max
from django.utils import timezone
from datetime import timedelta
from .models import LianJiaHouse
from .forms import CustomUserCreationForm, CustomAuthenticationForm
import json
import requests
import time


# ==================== 登录注册相关视图 ====================

# 首页 - 需要登录才能访问
@login_required(login_url='main_app:login')  # 修改这里：添加命名空间前缀
def index(request):
    """
    首页 - 需要登录，并显示房屋数据
    """
    # 获取房屋数据
    total_houses = LianJiaHouse.objects.count()
    district_count = LianJiaHouse.objects.values('district').distinct().count()

    try:
        avg_price_result = LianJiaHouse.objects.aggregate(avg_price=Avg('unit_price'))
        avg_price = avg_price_result['avg_price']
    except:
        avg_price = 0

    recent_houses = LianJiaHouse.objects.all().order_by('-crawl_time')[:6]

    # 构建上下文
    context = {
        # 用户信息
        'username': request.user.username,
        'is_authenticated': request.user.is_authenticated,
        'user': request.user,  # 完整的user对象

        # 房屋数据
        'total_houses': total_houses,
        'district_count': district_count,
        'avg_price': round(avg_price, 2) if avg_price else 0,
        'recent_houses': recent_houses,
        'last_login': request.user.last_login,
        'date_joined': request.user.date_joined,
    }
    return render(request, 'main_app/index.html', context)  # 修改这里：添加模板路径前缀


# 注册视图
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # 自动登录用户
            login(request, user)

            # 记录用户注册信息到控制台
            print(f"新用户注册成功: {user.username}, 邮箱: {user.email}, 时间: {user.date_joined}")

            # 跳转到首页
            return redirect('main_app:index')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


# 登录视图
def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)

                # 记录登录信息
                print(f"用户登录: {user.username}, 时间: {user.last_login}")

                # 检查是否有next参数
                next_url = request.GET.get('next', None)
                if next_url:
                    return redirect(next_url)
                return redirect('main_app:index')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})


# 登出视图
def logout_view(request):
    logout(request)
    return redirect('main_app:login')


# ==================== 房屋数据相关视图 ====================

@login_required(login_url='main_app:login')  # 修改这里
def house_list(request):
    """房屋列表页 - 需要登录"""
    houses = LianJiaHouse.objects.all().order_by('-crawl_time')
    search_query = request.GET.get('search', '')
    district_filter = request.GET.get('district', '')
    layout_filter = request.GET.get('layout', '')

    if search_query:
        houses = houses.filter(title__icontains=search_query)
    if district_filter:
        houses = houses.filter(district=district_filter)
    if layout_filter:
        houses = houses.filter(layout__icontains=layout_filter)

    districts = LianJiaHouse.objects.values_list('district', flat=True).distinct()
    layouts = LianJiaHouse.objects.values_list('layout', flat=True).distinct()
    paginator = Paginator(houses, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'houses': page_obj,
        'districts': districts,
        'layouts': layouts,
        'search_query': search_query,
        'district_filter': district_filter,
        'layout_filter': layout_filter,
    }
    return render(request, 'main_app/house_list.html', context)


@login_required(login_url='main_app:login')  # 修改这里
def dashboard(request):
    """数据大屏 - 需要登录"""
    total_houses = LianJiaHouse.objects.count()
    district_count = LianJiaHouse.objects.values('district').distinct().count()
    try:
        avg_price_result = LianJiaHouse.objects.aggregate(avg_price=Avg('unit_price'))
        avg_price = avg_price_result['avg_price']
    except:
        avg_price = 0
    today = timezone.now().date()
    today_count = LianJiaHouse.objects.filter(crawl_time__date=today).count()
    last_update = LianJiaHouse.objects.order_by('-crawl_time').first()

    # 添加上下文变量，包含时间戳
    context = {
        'total_houses': total_houses,
        'district_count': district_count,
        'avg_price': round(avg_price, 2) if avg_price else 0,
        'today_count': today_count,
        'last_update': last_update.crawl_time if last_update else timezone.now(),
        'timestamp': int(time.time()),  # 添加时间戳，避免浏览器缓存
    }
    return render(request, 'main_app/dashboard.html', context)


@login_required(login_url='main_app:login')  # 修改这里
def professional_dashboard(request):
    """专业版数据大屏 - 需要登录"""
    total_houses = LianJiaHouse.objects.count()
    district_count = LianJiaHouse.objects.values('district').distinct().count()
    try:
        price_stats = LianJiaHouse.objects.aggregate(
            avg_price=Avg('unit_price'),
            max_price=Max('unit_price'),
            min_price=Min('unit_price'),
            avg_total=Avg('total_price'),
            total_value=Sum('total_price')
        )
        avg_price = price_stats['avg_price']
        max_price = price_stats['max_price']
        min_price = price_stats['min_price']
        avg_total = price_stats['avg_total']
    except:
        avg_price = max_price = min_price = avg_total = 0

    district_stats = LianJiaHouse.objects.values('district').annotate(
        count=Count('id'),
        avg_price=Avg('unit_price'),
        avg_total=Avg('total_price')
    ).order_by('-count')
    layout_stats = LianJiaHouse.objects.values('layout').annotate(
        count=Count('id')
    ).order_by('-count')[:10]

    price_ranges = [
        (0, 200), (200, 400), (400, 600),
        (600, 800), (800, 1000), (1000, 10000)
    ]
    price_distribution = []
    for min_price, max_price in price_ranges:
        count = LianJiaHouse.objects.filter(
            total_price__gte=min_price,
            total_price__lt=max_price
        ).count()
        price_distribution.append({
            'range': f'{min_price}-{max_price}万',
            'count': count
        })

    area_ranges = [
        (0, 50), (50, 70), (70, 90),
        (90, 120), (120, 150), (150, 1000)
    ]
    area_distribution = []
    for min_area, max_area in area_ranges:
        count = LianJiaHouse.objects.filter(
            area__gte=min_area,
            area__lt=max_area
        ).count()
        area_distribution.append({
            'range': f'{min_area}-{max_area}㎡',
            'count': count
        })

    today = timezone.now().date()
    today_count = LianJiaHouse.objects.filter(crawl_time__date=today).count()
    last_update = LianJiaHouse.objects.order_by('-crawl_time').first()

    context = {
        'total_houses': total_houses,
        'district_count': district_count,
        'avg_price': round(avg_price, 2) if avg_price else 0,
        'max_price': round(max_price, 2) if max_price else 0,
        'min_price': round(min_price, 2) if min_price else 0,
        'avg_total': round(avg_total, 2) if avg_total else 0,
        'today_count': today_count,
        'last_update': last_update.crawl_time if last_update else timezone.now(),
        'district_stats': list(district_stats),
        'layout_stats': list(layout_stats),
        'price_distribution': price_distribution,
        'area_distribution': area_distribution,
    }
    return render(request, 'main_app/professional_dashboard.html', context)


@login_required(login_url='main_app:login')  # 修改这里
def echarts_dashboard(request):
    """ECharts动态可视化大屏 - 需要登录"""
    try:
        total_houses = LianJiaHouse.objects.count()
        avg_unit_price = LianJiaHouse.objects.aggregate(avg=Avg('unit_price'))['avg'] or 0
        avg_area = LianJiaHouse.objects.aggregate(avg=Avg('area'))['avg'] or 0
        city_stats = list(LianJiaHouse.objects.values('city').annotate(
            count=Count('id'),
            avg_price=Avg('unit_price'),
            avg_area=Avg('area')
        ).order_by('-count'))

        price_ranges = [
            {'name': '0-100万', 'min': 0, 'max': 100,
             'count': LianJiaHouse.objects.filter(total_price__lte=100).count()},
            {'name': '100-300万', 'min': 100, 'max': 300,
             'count': LianJiaHouse.objects.filter(total_price__gt=100, total_price__lte=300).count()},
            {'name': '300-500万', 'min': 300, 'max': 500,
             'count': LianJiaHouse.objects.filter(total_price__gt=300, total_price__lte=500).count()},
            {'name': '500万以上', 'min': 500, 'max': 99999,
             'count': LianJiaHouse.objects.filter(total_price__gt=500).count()},
        ]
        layout_stats = list(LianJiaHouse.objects.values('layout').annotate(
            count=Count('id')
        ).order_by('-count')[:10])
        area_ranges = [
            {'name': '0-50㎡', 'min': 0, 'max': 50, 'count': LianJiaHouse.objects.filter(area__lte=50).count()},
            {'name': '50-80㎡', 'min': 50, 'max': 80,
             'count': LianJiaHouse.objects.filter(area__gt=50, area__lte=80).count()},
            {'name': '80-120㎡', 'min': 80, 'max': 120,
             'count': LianJiaHouse.objects.filter(area__gt=80, area__lte=120).count()},
            {'name': '120-150㎡', 'min': 120, 'max': 150,
             'count': LianJiaHouse.objects.filter(area__gt=120, area__lte=150).count()},
            {'name': '150㎡以上', 'min': 150, 'max': 9999, 'count': LianJiaHouse.objects.filter(area__gt=150).count()},
        ]
        scatter_data = list(LianJiaHouse.objects.filter(
            area__isnull=False,
            unit_price__isnull=False
        ).values('area', 'unit_price', 'city')[:200])

        context = {
            'total_houses': total_houses,
            'avg_unit_price': round(avg_unit_price),
            'avg_area': round(avg_area),
            'city_count': len(city_stats),
            'city_stats_json': json.dumps(city_stats, ensure_ascii=False),
            'price_ranges_json': json.dumps(price_ranges, ensure_ascii=False),
            'layout_stats_json': json.dumps(layout_stats, ensure_ascii=False),
            'area_ranges_json': json.dumps(area_ranges, ensure_ascii=False),
            'scatter_data_json': json.dumps(scatter_data, ensure_ascii=False),
        }
        return render(request, 'main_app/echarts_dashboard.html', context)
    except Exception as e:
        return render(request, 'main_app/error.html', {'error_message': str(e)})


# ==================== AI分析功能 ====================

def call_moonshot_api(question, total_houses, avg_price, expensive_district, cheap_district):
    """
    调用 Moonshot AI 官方 API
    """
    # 注意：这里需要替换成你自己的 API Key
    api_key = "sk-kzEpDrLD8t6lymy0Fc53GEasCqBMZLk2vcbThngoK8bln7t2"
    api_url = "https://api.moonshot.cn/v1/chat/completions"

    # 构建专业的提示词
    system_prompt = f"""你是一个专业的房地产数据分析AI助手。请根据以下北京房产市场的数据背景来回答问题：
    - 分析样本：当前数据库包含 {total_houses} 条真实房源信息。
    - 市场价格：全市平均单价约为 {avg_price} 元/平方米。
    - 区域对比：房价最高的区域是 {expensive_district}，房价相对较低的区域是 {cheap_district}。

    你的回答需要专业、客观，并尽量结合数据背景。如果问题超出已知数据范围，可以基于一般市场规律进行分析，并说明情况。回答请保持清晰有条理。"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "moonshot-v1-8k",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        "stream": False
    }

    try:
        response = requests.post(api_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()

        # 从返回的JSON中提取AI的回答文本
        ai_answer = result.get('choices', [{}])[0].get('message', {}).get('content', '')

        if ai_answer:
            return ai_answer.strip()
        else:
            return "抱歉，AI助手暂时无法生成回答，请稍后再试。"

    except requests.exceptions.ConnectionError:
        return "网络连接失败，请检查你的网络设置。"
    except requests.exceptions.Timeout:
        return "请求超时，可能是服务器响应慢或网络问题。"
    except requests.exceptions.RequestException as e:
        print(f"[Moonshot API 错误] 请求失败: {e}")
        return f"网络请求出现错误，请稍后重试。"
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"[Moonshot API 错误] 解析响应失败: {e}")
        return "解析AI回复时出现意外错误。"


@login_required(login_url='main_app:login')  # 修改这里
def ai_analysis(request):
    """AI智能分析页面 - 需要登录"""
    # 从数据库获取数据进行分析
    houses = LianJiaHouse.objects.all()
    total_houses = houses.count()

    # 1. 基本统计分析
    try:
        avg_price = houses.aggregate(Avg('unit_price'))['unit_price__avg']
        avg_price = round(avg_price, 2) if avg_price else 0
    except:
        avg_price = 0

    # 2. 按区域分析
    try:
        districts = houses.values('district').annotate(
            count=Count('id'),
            avg_price=Avg('unit_price')
        ).order_by('-avg_price')
        if districts:
            expensive_district = districts[0]['district']
            cheap_district = districts[len(districts) - 1]['district']
        else:
            expensive_district = "暂无数据"
            cheap_district = "暂无数据"
    except:
        expensive_district = "暂无数据"
        cheap_district = "暂无数据"

    # 3. 处理AI问答
    answer = ""
    if request.method == 'POST':
        question = request.POST.get('question', '').strip()
        if question:
            answer = call_moonshot_api(question, total_houses, avg_price, expensive_district, cheap_district)
            print(f"[AI问答] 问题: {question[:50]}... | 答案长度: {len(answer)}")

    # 4. 传递给模板的上下文
    context = {
        'avg_price': avg_price,
        'expensive_district': expensive_district,
        'cheap_district': cheap_district,
        'recommend_district': expensive_district,
        'return_rate': "5-8",
        'best_time': "2024年第二季度",
        'answer': answer,
        'total_houses': total_houses,
    }
    return render(request, 'main_app/ai_analysis.html', context)


# ==================== 辅助视图 ====================

def debug_auth(request):
    """调试认证状态"""
    info = f"""
    用户认证状态：
    是否认证：{request.user.is_authenticated}
    用户名：{request.user.username}
    用户ID：{request.user.id}
    """
    return HttpResponse(info)