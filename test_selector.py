import requests
from bs4 import BeautifulSoup


def test_selectors():
    url = "https://bj.lianjia.com/ershoufang/chaoyang/pg1/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    print("🌐 正在请求链家页面...")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"✅ 请求成功，状态码: {response.status_code}")

        soup = BeautifulSoup(response.text, 'html.parser')

        # 检查页面标题
        title = soup.find('title')
        if title:
            print(f"📄 页面标题: {title.text}")

        # 测试各种选择器
        selectors = [
            '.sellListContent li',
            '.content__list--item',
            '.house-lst li',
            '.resblock-list',
            '[class*="list"] li',
            '.ershoufang-list li',
            '.lj-house-item',
            '.info-clear',
            '.clear',
            '.item'
        ]

        print("\n🔍 测试各种选择器...")
        found_any = False
        for selector in selectors:
            elements = soup.select(selector)
            print(f"选择器 '{selector}': 找到 {len(elements)} 个元素")

            if elements:
                found_any = True
                for i, elem in enumerate(elements[:2]):  # 只显示前2个
                    text = elem.get_text(strip=True)[:100]  # 只取前100字符
                    print(f"  元素 {i + 1}: {text}")

        if not found_any:
            print("\n❌ 所有选择器都没有找到房源数据！")
            print("💡 可能的原因：")
            print("   - 页面需要登录")
            print("   - 触发了反爬虫机制")
            print("   - 页面结构已完全改变")

    except Exception as e:
        print(f"❌ 请求失败: {e}")


# 运行测试
if __name__ == "__main__":
    test_selectors()