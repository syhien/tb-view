import time
import random
import os
import sys
from playwright.sync_api import sync_playwright, Playwright, Error as PlaywrightError

# ----- 配置 -----
# 包含URL列表的文件名
URL_FILE = "urls.txt"
# 每个页面最短浏览时间（秒）
MIN_BROWSE_SECONDS = 12
# 每个页面最长浏览时间（秒）
MAX_BROWSE_SECONDS = 20
# 两次滚动之间的最短间隔时间（秒）
MIN_SCROLL_PAUSE = 1.5
# 两次滚动之间的最长间隔时间（秒）
MAX_SCROLL_PAUSE = 3.5
# 页面加载超时时间（毫秒）
PAGE_LOAD_TIMEOUT = 60000

def browse_urls_from_file(playwright: Playwright):
    """
    启动一个浏览器实例，从`urls.txt`文件中读取URL列表，
    并模拟人类行为逐一访问和滚动浏览这些页面。

    Args:
        playwright (Playwright): Playwright的实例。
    """
    # 步骤 1: 检查 `urls.txt` 文件是否存在
    if not os.path.exists(URL_FILE):
        print(f"错误: 在当前目录下未找到 '{URL_FILE}' 文件。")
        # 如果文件不存在，创建一个示例文件以供参考
        try:
            with open(URL_FILE, 'w', encoding='utf-8') as f:
                f.write("https://www.google.com\n")
                f.write("https://github.com/\n")
            print(f"已为您创建一个示例 '{URL_FILE}' 文件，请填入您需要访问的网址。")
        except IOError as e:
            print(f"创建示例文件失败: {e}")
        return

    # 步骤 2: 从文件中读取所有有效的URL
    try:
        with open(URL_FILE, 'r', encoding='utf-8') as f:
            # 过滤掉空行和无效行
            urls = [line.strip() for line in f if line.strip() and line.startswith(('http://', 'https://'))]
    except IOError as e:
        print(f"读取 '{URL_FILE}' 文件时发生错误: {e}")
        return

    if not urls:
        print(f"'{URL_FILE}' 文件为空或不包含任何有效的URL。请确保每行都是以 http:// 或 https:// 开头的网址。")
        return

    print(f"成功加载 {len(urls)} 个URL。准备开始浏览...")

    # 步骤 3: 启动浏览器
    # headless=False 使浏览器界面可见，以便观察脚本执行过程
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(
        # 模拟一个常见的浏览器 User-Agent，减少被网站识别为机器人的风险
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    )
    page = context.new_page()

    try:
        # 步骤 4: 遍历并访问列表中的每一个URL
        for index, url in enumerate(urls):
            print("-" * 50)
            print(f"[{index + 1}/{len(urls)}] 正在导航至: {url}")

            try:
                # 导航到指定页面，并设置超时
                page.goto(url, timeout=PAGE_LOAD_TIMEOUT)
                print(f"页面加载成功。")

                # 步骤 5: 随机持续浏览一段时间
                browse_duration = random.randint(MIN_BROWSE_SECONDS, MAX_BROWSE_SECONDS)
                print(f"将在此页面停留 {browse_duration} 秒并随机滚动...")

                start_time = time.time()
                while time.time() - start_time < browse_duration:
                    # 步骤 6: 模拟随机的鼠标滚轮滚动
                    # 随机决定是向下滚动还是向上滚动
                    scroll_amount = random.randint(400, 1200) * random.choice([-1, 1])
                    
                    page.mouse.wheel(0, scroll_amount)
                    direction = "向下" if scroll_amount > 0 else "向上"
                    print(f"  -> 滚动鼠标 ({direction} {abs(scroll_amount)} 像素)")
                    
                    # 随机暂停一段时间，使行为更像人类
                    pause_interval = random.uniform(MIN_SCROLL_PAUSE, MAX_SCROLL_PAUSE)
                    time.sleep(pause_interval)

                print(f"完成浏览: {url}")

            except PlaywrightError as e:
                print(f"错误: 无法打开或浏览 {url}。原因: {e}")
                # 遇到错误时，跳过当前URL，继续处理下一个
                continue
    
    finally:
        # 步骤 7: 确保所有操作结束后关闭浏览器
        print("-" * 50)
        print("所有URL已处理完毕。正在关闭浏览器...")
        browser.close()

def main():
    """
    脚本主入口函数
    """
    # 设置控制台输出编码为 UTF-8，防止在某些终端下出现乱码
    if sys.stdout.encoding != 'utf-8':
         sys.stdout.reconfigure(encoding='utf-8')

    try:
        with sync_playwright() as playwright:
            browse_urls_from_file(playwright)
    except Exception as e:
        print(f"脚本执行过程中发生未预料的错误: {e}")


if __name__ == "__main__":
    main()
