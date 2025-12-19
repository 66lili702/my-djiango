import requests
import csv
import time
from bs4 import BeautifulSoup
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def multi_city_crawler_safe():
    """安全的多城市爬虫 - 每个城市爬5页，避免触发反爬"""

    cities = [
        ('bj', '北京'),
        ('sh', '上海'),
        ('gz', '广州'),
        ('sz', '深圳'),
        ('hz', '杭州'),
        ('nj', '南京'),
        ('wh', '武汉'),
        ('cd', '成都')
    ]

    all_houses = []

    for city_code, city_name in cities:
        logger.info(f"\n🚀 开始爬取 {city_name} 数据...")

        city_houses = crawl_city_safe(city_code, city_name, max_pages=5)
        all_houses.extend(city_houses)

        logger.info(f"✅ {city_name} 完成，获取 {len(city_houses)} 条数据")

        # 城市间较长延迟，避免被封
        delay = random.uniform(10, 20)
        logger.info(f"等待 {delay:.1f} 秒后继续下一个城市...")
        time.sleep(delay)

    # 保存所有数据
    filename = f'multi_city_houses_{len(all_houses)}.csv'
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(
            ['城市', '标题', '总价(万)', '单价(元/平)', '户型', '面积(平)', '朝向', '装修', '楼层', '年份', '小区',
             '区域', '链接'])

        for house in all_houses:
            writer.writerow([
                house['city'],
                house['title'],
                house['total_price'],
                house['unit_price'],
                house['layout'],
                house['area'],
                house['direction'],
                house['decoration'],
                house['floor'],
                house['year'],
                house['community'],
                house['district'],
                house['link']
            ])

    logger.info(f"\n🎉 所有城市爬取完成！总共获取 {len(all_houses)} 条数据")
    logger.info(f"📁 数据文件: {filename}")

    return len(all_houses)


def crawl_city_safe(city_code, city_name, max_pages=5):
    """安全爬取单个城市数据"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    }

    session = requests.Session()
    session.headers.update(headers)

    city_houses = []

    for page in range(1, max_pages + 1):
        logger.info(f"  正在爬取第 {page} 页...")

        # 构造URL
        if page == 1:
            url = f'https://{city_code}.lianjia.com/ershoufang/'
        else:
            url = f'https://{city_code}.lianjia.com/ershoufang/pg{page}/'

        try:
            # 随机延迟
            time.sleep(random.uniform(2, 4))

            response = session.get(url, timeout=10)
            response.encoding = 'utf-8'

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # 检查是否被限制
                if "没有找到合适的房源" in response.text or "访问验证" in response.text:
                    logger.warning(f"  ⚠️  {city_name} 第 {page} 页被限制，跳过")
                    break

                house_list = soup.select('.sellListContent li')
                logger.info(f"  第 {page} 页找到 {len(house_list)} 个房屋")

                if len(house_list) == 0:
                    logger.warning(f"  ⚠️  {city_name} 第 {page} 页没有数据，停止")
                    break

                page_count = 0
                for house in house_list:
                    house_data = extract_house_safe(house)
                    if house_data:
                        house_data['city'] = city_name
                        city_houses.append(house_data)
                        page_count += 1

                logger.info(f"  ✅ 第{page}页提取 {page_count} 个房屋")

            else:
                logger.warning(f"  ❌ {city_name} 第 {page} 页请求失败")
                break

        except Exception as e:
            logger.error(f"  ❌ {city_name} 第 {page} 页出错: {e}")
            break

    return city_houses


def extract_house_safe(house_element):
    """安全提取房屋数据"""
    try:
        data = {}

        # 标题和链接
        title_elem = house_element.select_one('.title a')
        if not title_elem:
            return None
        data['title'] = title_elem.text.strip()
        data['link'] = title_elem.get('href', '')

        # 价格
        total_price_elem = house_element.select_one('.totalPrice span')
        data['total_price'] = total_price_elem.text.strip() if total_price_elem else ""

        unit_price_elem = house_element.select_one('.unitPrice')
        data['unit_price'] = unit_price_elem.text.strip() if unit_price_elem else ""

        # 房屋信息
        house_info_elem = house_element.select_one('.houseInfo')
        if house_info_elem:
            info_parts = house_info_elem.text.strip().split('|')
            data['layout'] = info_parts[0].strip() if len(info_parts) > 0 else ""
            data['area'] = info_parts[1].strip() if len(info_parts) > 1 else ""
            data['direction'] = info_parts[2].strip() if len(info_parts) > 2 else ""
            data['decoration'] = info_parts[3].strip() if len(info_parts) > 3 else ""
            data['floor'] = info_parts[4].strip() if len(info_parts) > 4 else ""
            data['year'] = info_parts[5].strip() if len(info_parts) > 5 else ""

        # 位置信息
        position_elem = house_element.select_one('.positionInfo')
        if position_elem:
            position_info = position_elem.text.strip()
            position_parts = position_info.split('-')
            data['community'] = position_parts[0].strip() if len(position_parts) > 0 else ""
            data['district'] = position_parts[1].strip() if len(position_parts) > 1 else ""

        return data

    except Exception:
        return None


# 运行多城市爬虫
if __name__ == "__main__":
    total_count = multi_city_crawler_safe()
    print(f"\n最终结果: 成功爬取 {total_count} 条房屋数据！")