import asyncio
from playwright.async_api import async_playwright
import re
import time
import base64
import os
import io
import sys
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import traceback
from .browser_manager import BrowserManager

if getattr(sys, "frozen", False):
    # 禁用 Playwright 的日志输出
    os.environ["PWDEBUG"] = "0"
    os.environ["DEBUG"] = "0"
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"


# 处理打包后的GUI版本没有控制台的问题
class SafePrint:
    def __init__(self):
        self.has_console = hasattr(sys, "stdout") and sys.stdout is not None

    def write(self, data):
        if self.has_console:
            try:
                sys.stdout.write(data)
            except:
                pass

    def flush(self):
        if self.has_console:
            try:
                sys.stdout.flush()
            except:
                pass


# 如果是打包的GUI版本，重定向输出
if getattr(sys, "frozen", False):
    # 创建空的文件对象，避免None引起的问题
    if not sys.stdout:
        sys.stdout = io.StringIO()
    if not sys.stderr:
        sys.stderr = io.StringIO()


class NetEaseCrawler:
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.is_initialized = False
        self.processed_ids = set()
        self.stop_crawling = False
        self.browser_manager = BrowserManager()

    def _safe_print(self, message):
        """安全的打印函数，避免在GUI版本中出现问题"""
        try:
            print(message)
        except:
            pass

    async def initialize(self, ui=None):
        if self.is_initialized:
            self._safe_print("[Crawler] 浏览器已初始化，跳过")
            return

        self._safe_print("[Crawler] 正在初始化浏览器...")
        if ui:
            ui.add_update("status", message="检查浏览器...")

        # 获取浏览器路径
        browser_path = self.browser_manager.get_executable_path()
        self._safe_print(f"[Crawler] 浏览器路径: {browser_path}")

        if not browser_path:
            error_msg = "未找到浏览器可执行文件"
            if ui:
                ui.add_update("status", message=f"错误: {error_msg}")
            raise Exception(error_msg)

        # 验证文件是否存在
        if not os.path.exists(browser_path):
            error_msg = f"浏览器文件不存在: {browser_path}"
            if ui:
                ui.add_update("status", message=f"错误: {error_msg}")
            raise Exception(error_msg)

        try:
            # 启动 Playwright
            self._safe_print("[Crawler] 启动Playwright...")
            if ui:
                ui.add_update("status", message="启动浏览器框架...")
            self.playwright = await async_playwright().start()
            self._safe_print("[Crawler] Playwright启动成功")

            # 创建浏览器实例 - 使用更多调试选项
            launch_options = {
                "executable_path": browser_path,
                "headless": True,
                "args": [
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-accelerated-2d-canvas",
                    "--no-first-run",
                    "--no-zygote",
                    "--disable-gpu",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-features=IsolateOrigins,site-per-process",
                    "--disable-web-security",
                    "--disable-features=TranslateUI",
                    "--disable-extensions",
                ],
                "timeout": 30000,  # 30秒超时
                "handle_sigint": False,
                "handle_sigterm": False,
                "handle_sighup": False,
            }

            self._safe_print(f"[Crawler] 启动参数: {launch_options}")
            self._safe_print("[Crawler] 启动浏览器...")
            if ui:
                ui.add_update("status", message="启动浏览器进程...")

            try:
                self.browser = await self.playwright.chromium.launch(**launch_options)
                self._safe_print("[Crawler] 浏览器启动成功")
                if ui:
                    ui.add_update("status", message="浏览器启动成功")
            except Exception as e:
                self._safe_print(f"[Crawler] 浏览器启动失败: {e}")
                if ui:
                    ui.add_update("status", message=f"浏览器启动失败: {str(e)}")

                # 尝试使用默认参数
                self._safe_print("[Crawler] 尝试使用简化参数...")
                launch_options = {
                    "executable_path": browser_path,
                    "headless": True,
                    "args": ["--no-sandbox", "--disable-setuid-sandbox"],
                }
                self.browser = await self.playwright.chromium.launch(**launch_options)
                self._safe_print("[Crawler] 使用简化参数启动成功")
                if ui:
                    ui.add_update("status", message="使用简化参数启动成功")

            # 创建浏览器上下文
            self._safe_print("[Crawler] 创建浏览器上下文...")
            if ui:
                ui.add_update("status", message="创建浏览器上下文...")
            self.context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
                locale="zh-CN",
                timezone_id="Asia/Shanghai",
                accept_downloads=False,
                bypass_csp=True,
            )
            self._safe_print("[Crawler] 上下文创建成功")

            # 创建新页面
            self._safe_print("[Crawler] 创建新页面...")
            if ui:
                ui.add_update("status", message="创建新页面...")
            self.page = await self.context.new_page()
            self._safe_print("[Crawler] 页面创建成功")

            # 设置页面超时
            self.page.set_default_timeout(30000)  # 30秒

            self.is_initialized = True
            self._safe_print("[Crawler] 浏览器初始化完成")
            if ui:
                ui.add_update("status", message="浏览器初始化完成")

        except Exception as e:
            error_msg = f"初始化失败: {str(e)}"
            self._safe_print(f"[Crawler] {error_msg}")
            if not getattr(sys, "frozen", False):
                traceback.print_exc()

            if ui:
                ui.add_update("status", message=f"错误: {error_msg}")

            # 清理资源
            if hasattr(self, "browser") and self.browser:
                try:
                    await self.browser.close()
                except:
                    pass

            if hasattr(self, "playwright") and self.playwright:
                try:
                    await self.playwright.stop()
                except:
                    pass

            # 提供更详细的错误信息
            if "executable doesn't exist" in str(e):
                raise Exception(f"浏览器可执行文件不存在: {browser_path}")
            elif "Failed to launch" in str(e):
                raise Exception(f"浏览器启动失败，可能是权限问题: {e}")
            else:
                raise Exception(f"无法初始化浏览器: {e}")

    async def close(self):
        """关闭爬虫并清理所有资源"""
        try:
            # 停止任何正在进行的操作
            self.stop_crawling = True
            
            # 关闭页面
            if self.page:
                try:
                    await self.page.close()
                except:
                    pass
                self.page = None
            
            # 关闭上下文
            if self.context:
                try:
                    await self.context.close()
                except:
                    pass
                self.context = None
            
            # 关闭浏览器
            if self.browser:
                try:
                    await self.browser.close()
                except:
                    pass
                self.browser = None
            
            # 停止 Playwright
            if hasattr(self, 'playwright') and self.playwright:
                try:
                    await self.playwright.stop()
                except:
                    pass
                self.playwright = None
            
            self.is_initialized = False
            self._safe_print("浏览器已关闭")
            
        except Exception as e:
            self._safe_print(f"关闭爬虫时出错: {e}")

    async def crawl(self, url, ui):
        await self.initialize(ui)

        ui.add_update("status", message="正在初始化浏览器...")

        self._safe_print(f"开始访问URL: {url}")
        ui.add_update("status", message=f"正在加载页面: {url}")

        try:
            # 添加超时和错误处理
            await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
            self._safe_print("页面已加载完成")
            ui.add_update("status", message="页面加载完成，等待内容...")
        except Exception as e:
            error_msg = f"页面加载失败: {str(e)}"
            self._safe_print(f"[Crawler] {error_msg}")
            ui.add_update("status", message=error_msg)
            raise Exception(error_msg)

        # 等待iframe加载
        self._safe_print("等待iframe加载...")
        ui.add_update("status", message="等待iframe加载...")

        try:
            iframe = await self.page.wait_for_selector("#g_iframe", timeout=30000)
            self._safe_print("iframe已找到")
            ui.add_update("status", message="iframe已找到")
        except Exception as e:
            error_msg = f"找不到iframe: {str(e)}"
            self._safe_print(f"[Crawler] {error_msg}")
            ui.add_update("status", message=error_msg)

            # 尝试获取页面内容以调试
            page_content = await self.page.content()
            self._safe_print(f"页面内容长度: {len(page_content)}")
            if len(page_content) < 1000:
                self._safe_print(f"页面内容: {page_content[:500]}")

            raise ValueError("找不到#g_iframe，页面结构可能已改变")

        # 切换到iframe
        iframe = await self.page.query_selector("#g_iframe")
        iframe_content = await iframe.content_frame()
        self._safe_print("已切换到iframe内容")
        ui.add_update("status", message="已切换到iframe内容")

        # 等待一小段时间让页面内容加载
        ui.add_update("status", message="等待页面内容加载...")
        await asyncio.sleep(1)

        # 获取文章总数
        total_articles = None
        try:
            event_count_elem = await iframe_content.query_selector("#event_count2")
            if event_count_elem:
                total_articles_text = await event_count_elem.text_content()
                total_articles = int(total_articles_text.strip())
                self._safe_print(f"页面显示文章总数: {total_articles}")
                # 保存总文章数到ui对象，便于后续显示
                ui.total_articles = total_articles
                ui.add_update("total_count", count=total_articles)
                ui.add_update(
                    "status", message=f"用户共有 {total_articles} 篇文章，开始抓取..."
                )
            else:
                self._safe_print("找不到文章总数元素，将使用默认方式抓取")
                ui.add_update("status", message="开始抓取文章...")
        except Exception as e:
            self._safe_print(f"获取文章总数失败: {e}")
            ui.add_update("status", message="获取文章总数失败，继续抓取...")

        # 记录初始文章数量
        initial_article_count = len(ui.articles)

        # 初始扫描并提取所有文章
        ui.add_update(
            "status",
            message=f"开始提取文章... (总计: {total_articles if total_articles else '未知'})",
        )
        articles = await self.scan_all_articles(iframe_content, ui)

        # 检查第一次扫描是否找到新文章
        current_article_count = len(ui.articles)
        if current_article_count > initial_article_count:
            new_articles = current_article_count - initial_article_count
            self._safe_print(f"首次扫描发现 {new_articles} 篇文章，暂停5秒...")

            # 使用倒计时显示暂停状态
            for i in range(5, 0, -1):
                if self.stop_crawling:
                    break
                ui.add_update(
                    "status",
                    message=f"首次扫描发现 {new_articles} 篇文章，暂停中: {i}秒... (总计: {total_articles if total_articles else '未知'})",
                )
                await asyncio.sleep(1)

        # 如果没有终止，继续滚动页面获取所有文章
        if not self.stop_crawling:
            # 滚动页面以获取所有文章，或者直到超时
            await self.scroll_until_complete(iframe_content, ui, total_articles)

        if self.stop_crawling:
            ui.add_update(
                "status",
                message=f"爬取已手动终止，共获取 {len(ui.articles)} 篇文章 (总计: {total_articles if total_articles else '未知'})",
            )
        else:
            ui.add_update(
                "status",
                message=f"爬取完成，共获取 {len(ui.articles)} 篇文章 (总计: {total_articles if total_articles else '未知'})",
            )

        return ui.articles

    async def scroll_until_complete(self, frame, ui, total_articles=None):
        """滚动直到获取所有文章或者超时或者被手动终止"""
        try:
            # 获取初始高度
            last_height = await frame.evaluate("document.body.scrollHeight")
            self._safe_print(f"开始滚动，初始页面高度: {last_height}")

            # 记录上次文章数量和上次发现新文章的时间
            last_article_count = len(ui.articles)
            last_new_article_time = time.time()

            # 最大滚动次数和当前滚动次数
            max_scrolls = 100  # 设置一个较大的值，避免无限滚动
            current_scroll = 0

            while current_scroll < max_scrolls and not self.stop_crawling:
                current_scroll += 1
                self._safe_print(f"滚动 {current_scroll}...")

                # 如果已经获取到所有文章，停止滚动
                if total_articles is not None and len(ui.articles) >= total_articles:
                    self._safe_print(f"已获取所有 {total_articles} 篇文章，停止滚动")
                    ui.add_update(
                        "status",
                        message=f"已获取所有 {total_articles} 篇文章，停止滚动",
                    )
                    break

                # 检查是否超过3分钟没有新文章
                current_time = time.time()
                if current_time - last_new_article_time > 180:  # 3分钟 = 180秒
                    self._safe_print("超过3分钟没有发现新文章，停止滚动")
                    ui.add_update("status", message="超过3分钟没有发现新文章，停止滚动")
                    break

                ui.add_update(
                    "status",
                    message=f"滚动加载中 ({current_scroll})... 已获取 {len(ui.articles)} 篇文章 (总计: {total_articles if total_articles else '未知'})",
                )

                # 滚动到底部
                await frame.evaluate("window.scrollTo(0, document.body.scrollHeight)")

                # 短暂等待内容加载
                await asyncio.sleep(0.8)

                # 检查是否被终止
                if self.stop_crawling:
                    self._safe_print("爬取已被手动终止")
                    break

                # 获取新高度
                new_height = await frame.evaluate("document.body.scrollHeight")
                self._safe_print(f"滚动后新高度: {new_height}")

                # 如果高度没有变化，说明没有更多内容了
                if new_height == last_height:
                    self._safe_print("页面高度未变化，可能已到达底部")

                    # 再次检查是否已获取所有文章
                    if (
                        total_articles is not None
                        and len(ui.articles) >= total_articles
                    ):
                        self._safe_print(
                            f"已获取所有 {total_articles} 篇文章，停止滚动"
                        )
                        ui.add_update(
                            "status",
                            message=f"已获取所有 {total_articles} 篇文章，停止滚动",
                        )
                        break

                    # 多等待几次，可能只是暂时没有加载
                    if current_scroll % 3 == 0:  # 每隔3次滚动检查一下
                        self._safe_print("尝试再滚动几次...")
                        ui.add_update(
                            "status", message="页面似乎已到底部，再尝试几次..."
                        )

                # 滚动后扫描新文章
                self._safe_print("开始扫描新加载的内容...")
                ui.add_update(
                    "status",
                    message=f"扫描新内容... (总计: {total_articles if total_articles else '未知'})",
                )
                await self.scan_all_articles(frame, ui)

                # 检查是否有新文章
                current_article_count = len(ui.articles)
                if current_article_count > last_article_count:
                    new_articles = current_article_count - last_article_count
                    self._safe_print(f"发现 {new_articles} 篇新文章，暂停5秒...")

                    # 更新最后发现新文章的时间
                    last_new_article_time = time.time()

                    # 使用倒计时显示暂停状态
                    for i in range(5, 0, -1):
                        if self.stop_crawling:
                            break
                        ui.add_update(
                            "status",
                            message=f"发现 {new_articles} 篇新文章，暂停中: {i}秒...  (总计: {total_articles if total_articles else '未知'})",
                        )
                        await asyncio.sleep(1)

                    last_article_count = current_article_count

                last_height = new_height

            self._safe_print("滚动完成")
        except Exception as e:
            self._safe_print(f"滚动加载出错: {e}")
            if not getattr(sys, "frozen", False):
                traceback.print_exc()
            ui.add_update("status", message=f"滚动加载出错: {str(e)}")

    async def scan_all_articles(self, frame, ui):
        """一次性扫描并提取所有文章，采用和油猴脚本类似的方法"""
        # 获取整个iframe的HTML内容，一次性处理
        html_content = await frame.content()
        self._safe_print(f"获取到iframe HTML内容，长度: {len(html_content)}")

        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(html_content, "html.parser")

        # 查找所有dcntc元素
        dcntc_elements = soup.select(".dcntc")
        self._safe_print(f"找到 {len(dcntc_elements)} 个dcntc元素")

        articles = []
        new_count = 0

        for i, elem in enumerate(dcntc_elements):
            try:
                ui.add_update(
                    "status", message=f"处理文章 {i+1}/{len(dcntc_elements)}..."
                )

                # 提取时间
                time_elem = elem.select_one(".time")
                if not time_elem:
                    continue

                time_link = time_elem.select_one("a")
                if time_link:
                    time_text = time_link.get_text().strip()
                else:
                    time_text = time_elem.get_text().strip()

                # 提取文本内容 - 保留HTML
                text_elem = elem.select_one(".text")
                if not text_elem:
                    continue

                # 获取内部HTML
                text_html = "".join(str(c) for c in text_elem.contents)
                text_html = text_html.strip()

                # 生成文章ID
                article_id = self.generate_element_id(time_text, text_html)

                # 检查是否已处理过
                if article_id in self.processed_ids:
                    continue

                # 提取歌曲信息
                song = self.extract_song_info(elem)

                # 提取图片URL
                images = self.extract_image_urls(elem)

                # 创建文章对象
                article = {
                    "id": article_id,
                    "time": time_text,
                    "text": text_html,
                    "song": song,
                    "images": images,
                }

                # 添加到处理过的ID集合
                self.processed_ids.add(article_id)
                articles.append(article)
                new_count += 1

                # 更新UI
                ui.add_update("new_article", article=article)
                self._safe_print(f"已处理文章 {i+1}: {time_text}")

            except Exception as e:
                self._safe_print(f"处理文章 {i+1} 时出错: {e}")
                if not getattr(sys, "frozen", False):
                    traceback.print_exc()

        self._safe_print(f"本次扫描共提取 {new_count} 篇新文章")
        return articles

    async def scroll_and_scan(self, frame, ui, max_scrolls=10):
        """滚动页面并扫描新文章，每次找到新文章后暂停5秒"""
        try:
            # 获取初始高度
            last_height = await frame.evaluate("document.body.scrollHeight")
            self._safe_print(f"开始滚动，初始页面高度: {last_height}")

            # 记录上次文章数量
            last_article_count = len(ui.articles)

            for i in range(max_scrolls):
                self._safe_print(f"滚动 {i+1}/{max_scrolls}...")
                ui.add_update("status", message=f"滚动加载中 ({i+1}/{max_scrolls})...")

                # 滚动到底部
                await frame.evaluate("window.scrollTo(0, document.body.scrollHeight)")

                # 短暂等待内容加载
                await asyncio.sleep(0.8)

                # 获取新高度
                new_height = await frame.evaluate("document.body.scrollHeight")
                self._safe_print(f"滚动后新高度: {new_height}")

                # 如果高度没有变化，说明没有更多内容了
                if new_height == last_height:
                    self._safe_print("页面高度未变化，停止滚动")
                    ui.add_update("status", message="已到达页面底部，没有更多内容")
                    break

                # 滚动后扫描新文章
                self._safe_print("开始扫描新加载的内容...")
                ui.add_update("status", message="扫描新内容...")
                await self.scan_all_articles(frame, ui)

                # 检查是否有新文章
                current_article_count = len(ui.articles)
                if current_article_count > last_article_count:
                    new_articles = current_article_count - last_article_count
                    self._safe_print(f"发现 {new_articles} 篇新文章，暂停5秒...")

                    # 使用倒计时显示暂停状态
                    for i in range(5, 0, -1):
                        ui.add_update(
                            "status",
                            message=f"发现 {new_articles} 篇新文章，暂停中: {i}秒...",
                        )
                        await asyncio.sleep(1)

                    last_article_count = current_article_count

                last_height = new_height

            self._safe_print("滚动完成")
        except Exception as e:
            self._safe_print(f"滚动加载出错: {e}")
            if not getattr(sys, "frozen", False):
                traceback.print_exc()
            ui.add_update("status", message=f"滚动加载出错: {str(e)}")

    def generate_element_id(self, time, text):
        """生成文章的唯一ID"""
        # 使用时间和文本的前30个字符
        text_part = re.sub(r"\s+", "", text[:30])
        return f"{time}-{text_part}"

    def extract_song_info(self, elem):
        """从BeautifulSoup元素中提取歌曲信息"""
        try:
            # 查找.src元素
            src_element = elem.select_one(".src")
            if not src_element:
                return None

            # 查找.scnt元素
            scnt_element = src_element.select_one(".scnt")
            if not scnt_element:
                return None

            # 提取歌曲标题
            title_element = scnt_element.select_one(".tit a")
            if not title_element:
                return None

            title = title_element.get_text().strip()
            song_href = title_element.get("href", "")
            song_url = f"https://music.163.com{song_href}" if song_href else ""

            # 提取歌手信息
            artist_element = scnt_element.select_one(".from a")
            if not artist_element:
                return None

            artist = artist_element.get_text().strip()
            artist_href = artist_element.get("href", "")
            artist_url = f"https://music.163.com{artist_href}" if artist_href else ""

            return {
                "title": title,
                "url": song_url,
                "artist": artist,
                "artistUrl": artist_url,
            }
        except Exception as e:
            self._safe_print(f"提取歌曲信息出错: {e}")
            return None

    def extract_image_urls(self, elem):
        """从BeautifulSoup元素中提取图片URL"""
        try:
            image_urls = []

            # 查找.pics .pic img元素
            image_elements = elem.select(".pics .pic img")

            if image_elements:
                for img in image_elements:
                    src = img.get("src")
                    if src:
                        # 处理URL
                        clean_src = src.split("?")[0].replace("http:", "https:")
                        if clean_src:
                            image_urls.append(clean_src)
                            self._safe_print(f"找到图片: {clean_src}")
            else:
                # 如果找不到缩略图，尝试查找封面图
                cover_img = elem.select_one(".cover .lnk img")
                if cover_img and cover_img.get("src"):
                    src = cover_img.get("src")
                    clean_src = src.split("?")[0].replace("http:", "https:")
                    if clean_src:
                        image_urls.append(clean_src)
                        self._safe_print(f"找到封面图: {clean_src}")

            return image_urls
        except Exception as e:
            self._safe_print(f"提取图片URL出错: {e}")
            return []

    async def convert_image_to_base64(self, url):
        """将图片URL转换为base64格式"""
        if not url:
            return ""

        try:
            # 确保URL使用https协议
            secure_url = url.replace("http:", "https:")

            # 打开新页面下载图片，避免影响主页面
            page = await self.context.new_page()
            try:
                # 设置10秒超时
                response = await asyncio.wait_for(page.goto(secure_url), timeout=10)
                if response.status == 200:
                    image_data = await response.body()
                    # 转换为base64
                    base64_data = base64.b64encode(image_data).decode("utf-8")
                    # 获取MIME类型
                    content_type = response.headers.get("content-type", "image/jpeg")
                    return f"data:{content_type};base64,{base64_data}"
                else:
                    self._safe_print(f"获取图片失败: {response.status} {secure_url}")
                    return ""
            except asyncio.TimeoutError:
                self._safe_print(f"获取图片超时: {secure_url}")
                return ""
            except Exception as e:
                self._safe_print(f"获取图片出错: {e}")
                if not getattr(sys, "frozen", False):
                    traceback.print_exc()
                return ""
            finally:
                await page.close()
        except Exception as e:
            self._safe_print(f"转换图片为base64时出错: {e}, URL: {url}")
            if not getattr(sys, "frozen", False):
                traceback.print_exc()
            return ""
