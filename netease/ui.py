import tkinter as tk
import sys
from tkinter import ttk, messagebox, filedialog
import threading
import asyncio
import queue
from .data_processor import process_html_text
from .exporter import export_to_html, copy_to_clipboard
from .browser_manager import BrowserManager
import traceback
import webbrowser
from PIL import Image, ImageTk
import io
import os


class NetEaseMusicUI:
    def __init__(self, master, crawler):
        self.master = master
        self.crawler = crawler
        self.articles = []
        self.crawling = False
        self.update_queue = queue.Queue()
        self.total_articles = None
        self.browser_manager = BrowserManager()
        
        # 添加爬虫线程引用
        self.crawler_thread = None

        # 设置
        self.settings = {"imageSize": 100, "useBase64Images": True}
        self.PROJECT_URL = "https://github.com/sansn0/netease-note-backup"

        # 用于存储控制台输出
        self.console_output = []

        # 创建UI组件
        self.create_widgets()

        # 设置窗口图标
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(script_dir, "resources", "icon.ico")
            if os.path.exists(icon_path):
                self.master.iconbitmap(icon_path)
        except Exception as e:
            print(f"无法加载图标: {str(e)}")

        # 设置窗口关闭事件处理
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 检查浏览器状态
        self.check_browser_status()

        # 设置定时器以处理队列中的更新
        self.process_updates()
        
    
    def on_closing(self):
        """窗口关闭事件处理"""
        # 如果正在爬取，先停止
        if self.crawling:
            response = messagebox.askquestion(
                "确认退出",
                "爬虫正在运行中，是否强制退出？",
                icon="warning"
            )
            
            if response == "yes":
                # 强制停止爬虫
                self.stop_crawling(force=True)
                # 等待线程结束
                if self.crawler_thread and self.crawler_thread.is_alive():
                    self.crawler_thread.join(timeout=2)  # 最多等待2秒
            else:
                return  # 取消关闭
        
        # 清理爬虫资源
        try:
            # 创建新的事件循环来关闭爬虫
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.crawler.close())
            loop.close()
        except Exception as e:
            print(f"关闭爬虫时出错: {e}")
        
        # 销毁窗口
        self.master.destroy()
        
        # 强制退出程序
        import os
        os._exit(0)

    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.master, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 添加工具栏框架
        toolbar_frame = ttk.Frame(main_frame)
        toolbar_frame.pack(fill=tk.X, pady=(0, 5))

        # 左侧为空白占位
        ttk.Label(toolbar_frame, text="").pack(side=tk.LEFT, expand=True, fill=tk.X)

        # 更新日志按钮
        self.changelog_btn = ttk.Button(
            toolbar_frame, text="项目地址", command=self.open_changelog
        )
        self.changelog_btn.pack(side=tk.LEFT, padx=2)

        # 关于作者按钮
        self.about_btn = ttk.Button(
            toolbar_frame, text="关于作者", command=self.show_about
        )
        self.about_btn.pack(side=tk.LEFT, padx=2)

        # URL输入框
        url_frame = ttk.Frame(main_frame)
        url_frame.pack(fill=tk.X, pady=5)

        ttk.Label(url_frame, text="网易云音乐用户ID:").pack(side=tk.LEFT)
        self.id_entry = ttk.Entry(url_frame, width=30)
        self.id_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.load_button = ttk.Button(
            url_frame, text="加载", command=self.start_crawling
        )
        self.load_button.pack(side=tk.LEFT)

        self.stop_button = ttk.Button(
            url_frame, text="终止", command=self.stop_crawling, state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # 浏览器状态和下载按钮
        browser_frame = ttk.Frame(main_frame)
        browser_frame.pack(fill=tk.X, pady=5)

        self.browser_status_label = ttk.Label(browser_frame, text="检查浏览器状态...")
        self.browser_status_label.pack(side=tk.LEFT)

        self.download_browser_button = ttk.Button(
            browser_frame,
            text="下载浏览器",
            command=self.download_browser,
            state=tk.DISABLED,
        )
        self.download_browser_button.pack(side=tk.LEFT, padx=10)

        # 下载进度条
        self.download_progress = ttk.Progressbar(
            browser_frame,
            mode="determinate",
            length=200,
            style="info.Horizontal.TProgressbar",
        )
        self.download_progress.pack(side=tk.LEFT, padx=10)
        self.download_progress.pack_forget()  # 初始隐藏

        self.download_progress_label = ttk.Label(browser_frame, text="")
        self.download_progress_label.pack(side=tk.LEFT)

        # 信息显示
        self.count_label = ttk.Label(main_frame, text="已检测到 0 篇文章")
        self.count_label.pack(anchor=tk.W, pady=5)

        # 范围选择
        range_frame = ttk.Frame(main_frame)
        range_frame.pack(fill=tk.X, pady=5)

        ttk.Label(range_frame, text="范围:").pack(side=tk.LEFT)
        self.start_range = ttk.Spinbox(range_frame, from_=1, to=1, width=5)
        self.start_range.pack(side=tk.LEFT, padx=5)
        ttk.Label(range_frame, text="到").pack(side=tk.LEFT)
        self.end_range = ttk.Spinbox(range_frame, from_=1, to=1, width=5)
        self.end_range.pack(side=tk.LEFT, padx=5)
        ttk.Button(range_frame, text="最大", command=self.set_max_range).pack(
            side=tk.LEFT, padx=5
        )

        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)

        self.copy_button = ttk.Button(
            button_frame, text="复制文本", command=self.copy_text
        )
        self.copy_button.pack(side=tk.LEFT, padx=5)

        self.export_button = ttk.Button(
            button_frame, text="导出HTML", command=self.export_html
        )
        self.export_button.pack(side=tk.LEFT, padx=5)

        # 设置区域
        settings_frame = ttk.LabelFrame(main_frame, text="设置")
        settings_frame.pack(fill=tk.X, pady=10)

        # 图片大小设置
        size_frame = ttk.Frame(settings_frame)
        size_frame.pack(fill=tk.X, pady=5)

        ttk.Label(size_frame, text="图片大小(px):").pack(side=tk.LEFT)
        self.size_spinbox = ttk.Spinbox(size_frame, from_=50, to=500, width=5)
        self.size_spinbox.delete(0, tk.END)
        self.size_spinbox.insert(0, self.settings["imageSize"])
        self.size_spinbox.pack(side=tk.LEFT, padx=5)

        # Base64选项
        self.base64_var = tk.BooleanVar(value=self.settings["useBase64Images"])
        base64_check = ttk.Checkbutton(
            settings_frame, text="将图片转为base64格式(推荐)", variable=self.base64_var
        )
        base64_check.pack(anchor=tk.W, pady=5)

        # 文章列表框
        list_frame = ttk.LabelFrame(main_frame, text="文章列表")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # 创建带滚动条的列表框
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.article_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.article_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.article_listbox.yview)

        # 状态栏
        self.status_var = tk.StringVar(value="等待加载...")
        status_bar = ttk.Label(
            main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=5)

    def check_browser_status(self):
        """检查浏览器状态 - 修改版本"""
        print("[UI] 检查浏览器状态...")

        # 强制重新创建 browser_manager 实例以刷新状态
        self.browser_manager = BrowserManager()

        if self.browser_manager.is_browser_installed():
            browser_path = self.browser_manager.get_executable_path()
            print(f"[UI] 找到浏览器: {browser_path}")

            # 判断浏览器来源
            if (
                not self.browser_manager.is_frozen
                and browser_path
                and "ms-playwright" in str(browser_path)
            ):
                status_text = "✓ 使用 Playwright 浏览器"
            else:
                status_text = "✓ 浏览器已安装"

            self.browser_status_label.config(text=status_text, foreground="green")
            self.download_browser_button.config(state=tk.DISABLED)
            self.load_button.config(state=tk.NORMAL)
        else:
            print("[UI] 未找到浏览器")
            self.browser_status_label.config(text="✗ 未找到浏览器", foreground="red")

            # 根据环境显示不同的按钮文本
            if self.browser_manager.is_frozen:
                button_text = "下载浏览器"
            else:
                button_text = "安装浏览器"

            self.download_browser_button.config(text=button_text, state=tk.NORMAL)
            self.load_button.config(state=tk.DISABLED)

        # 强制更新界面
        self.master.update_idletasks()
        print("[UI] 浏览器状态检查完成")

    def download_browser(self):
        """下载或安装浏览器"""
        if not self.browser_manager.is_frozen:
            # 开发环境：尝试使用 playwright install
            response = messagebox.askquestion(
                "安装浏览器",
                "是否运行 'poetry run playwright install chromium' 安装浏览器？\n"
                "如果失败，将尝试直接下载。",
                icon="question",
            )

            if response == "yes":
                self.status_var.set("正在通过 Playwright 安装浏览器...")

                # 尝试使用 playwright install
                def install_thread():
                    success = self.browser_manager.use_playwright_browser()
                    if success:
                        self.master.after(0, self.playwright_install_complete)
                    else:
                        # 如果失败，回退到下载方式
                        self.master.after(0, self.fallback_to_download)

                threading.Thread(target=install_thread, daemon=True).start()
                return

        # 打包环境或开发环境的回退方案：直接下载
        self.start_browser_download()

    def playwright_install_complete(self):
        """Playwright 安装完成"""
        self.status_var.set("浏览器安装完成")
        messagebox.showinfo("成功", "通过 Playwright 安装浏览器成功！")
        self.check_browser_status()

    def fallback_to_download(self):
        """回退到下载方式"""
        response = messagebox.askquestion(
            "Playwright 安装失败",
            "通过 Playwright 安装失败，是否直接下载浏览器？",
            icon="warning",
        )

        if response == "yes":
            self.start_browser_download()
        else:
            self.check_browser_status()

    def start_browser_download(self):
        """开始下载浏览器"""
        self.download_browser_button.config(state=tk.DISABLED, text="下载中...")
        self.download_progress.pack(side=tk.LEFT, padx=10)
        self.download_progress_label.config(text="准备下载...")

        # 启动下载线程
        threading.Thread(target=self.download_browser_thread, daemon=True).start()

    def download_browser_thread(self):
        """浏览器下载线程"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def download_with_progress():
            async def progress_callback(progress, downloaded, total):
                self.master.after(
                    0,
                    lambda: self.update_download_progress(progress, downloaded, total),
                )

            try:
                print("[UI] 开始下载浏览器...")
                await self.browser_manager.ensure_browser(progress_callback)
                print("[UI] 浏览器下载和安装完成")
                # 确保在主线程中执行UI更新
                self.master.after(0, self.download_complete)
            except Exception as e:
                print(f"[UI] 下载失败: {e}")
                self.master.after(0, lambda: self.download_failed(str(e)))

        try:
            loop.run_until_complete(download_with_progress())
        except Exception as e:
            print(f"[UI] 下载线程异常: {e}")
            self.master.after(0, lambda: self.download_failed(str(e)))
        finally:
            loop.close()

    def update_download_progress(self, progress, downloaded, total):
        """更新下载进度"""
        self.download_progress["value"] = progress

        # 格式化显示大小
        downloaded_mb = downloaded / (1024 * 1024)
        total_mb = total / (1024 * 1024)

        self.download_progress_label.config(
            text=f"{downloaded_mb:.1f}MB / {total_mb:.1f}MB ({progress:.1f}%)"
        )

    def download_complete(self):
        """下载完成 - 添加更多调试信息"""
        print("[UI] 进入download_complete方法")

        # 隐藏进度条
        self.download_progress.pack_forget()
        self.download_progress_label.config(text="")

        # 重置按钮状态
        self.download_browser_button.config(text="下载浏览器", state=tk.NORMAL)

        # 强制刷新浏览器管理器
        self.browser_manager = BrowserManager()

        # 检查浏览器是否真的安装成功
        if self.browser_manager.is_browser_installed():
            browser_path = self.browser_manager.get_executable_path()
            print(f"[UI] 浏览器安装成功，路径: {browser_path}")

            # 显示成功消息
            messagebox.showinfo("成功", f"浏览器下载并安装完成！\n路径: {browser_path}")
        else:
            print("[UI] 浏览器安装失败")
            messagebox.showwarning("警告", "浏览器下载完成但安装可能失败，请重试")

        # 强制刷新浏览器状态
        print("[UI] 刷新浏览器状态...")
        self.check_browser_status()

        # 强制更新界面
        self.master.update()

        print("[UI] download_complete完成")

    def download_failed(self, error):
        """下载失败"""
        self.download_progress.pack_forget()
        self.download_progress_label.config(text="")
        self.download_browser_button.config(text="下载浏览器", state=tk.NORMAL)

        messagebox.showerror("错误", f"浏览器下载失败：{error}")
        self.check_browser_status()

    def stop_crawling(self, force=False):
        """终止爬取过程"""
        if self.crawling or force:
            self.crawler.stop_crawling = True
            self.status_var.set("正在终止爬取...")
            self.stop_button.config(state=tk.DISABLED)
            
            if force:
                # 强制终止线程（虽然不是最佳实践，但在关闭时需要）
                if self.crawler_thread and self.crawler_thread.is_alive():
                    # 设置一个标志让线程知道需要立即退出
                    self.force_stop = True

    def process_updates(self):
        """处理来自爬虫的更新"""
        try:
            while not self.update_queue.empty():
                update = self.update_queue.get_nowait()
                update_type = update.get("type")

                if update_type == "articles":
                    self.articles = update.get("data", [])
                    self.update_article_display()
                elif update_type == "status":
                    message = update.get("message", "")
                    current_count = len(self.articles)

                    if "已获取" not in message and current_count > 0:
                        if not message.startswith(("处理文章", "图片", "正在处理")):
                            message = f"已获取 {current_count} 篇文章 - {message}"

                    if self.total_articles and "总计" not in message:
                        message += f" (总计: {self.total_articles})"

                    self.status_var.set(message)
                elif update_type == "new_article":
                    new_article = update.get("article")
                    if new_article:
                        self.articles.append(new_article)
                        self.count_label.config(
                            text=f"已检测到 {len(self.articles)} 篇文章"
                        )
                        self.article_listbox.insert(
                            tk.END,
                            f"{new_article['time']} - {self.get_short_text(new_article['text'])}",
                        )
                        self.update_range_inputs()
                elif update_type == "total_count":
                    self.total_articles = update.get("count")
        except queue.Empty:
            pass
        finally:
            self.master.after(200, self.process_updates)

    def get_short_text(self, html_text, max_length=50):
        """获取文本的简短版本用于显示"""
        text = process_html_text(html_text)
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text

    def update_article_display(self):
        """更新文章显示"""
        count = len(self.articles)
        self.count_label.config(text=f"已检测到 {count} 篇文章")
        self.update_range_inputs()

        self.article_listbox.delete(0, tk.END)
        for article in self.articles:
            self.article_listbox.insert(
                tk.END, f"{article['time']} - {self.get_short_text(article['text'])}"
            )

    def update_range_inputs(self):
        """更新范围输入框"""
        count = len(self.articles)
        self.start_range.config(from_=1, to=max(1, count))
        self.end_range.config(from_=1, to=max(1, count))

        current_end = self.end_range.get()
        if current_end == "1" and count > 1:
            self.end_range.delete(0, tk.END)
            self.end_range.insert(0, str(count))

    def add_update(self, update_type, **kwargs):
        """添加更新到队列"""
        update = {"type": update_type, **kwargs}
        self.update_queue.put(update)

        if update_type == "new_article":
            current_count = len(self.articles) + 1
            message = f"已获取 {current_count} 篇文章"
            if self.total_articles:
                message += f" (总计: {self.total_articles})"
            self.status_var.set(message)

    def start_crawling(self):
        if self.crawling:
            messagebox.showinfo("提示", "已经在爬取中，请等待完成")
            return

        # 再次检查浏览器
        if not self.browser_manager.is_browser_installed():
            response = messagebox.askquestion(
                "未找到浏览器", "未检测到浏览器，是否立即下载？", icon="warning"
            )
            if response == "yes":
                self.download_browser()
            return

        user_id = self.id_entry.get().strip()
        if not user_id or not user_id.isdigit():
            messagebox.showerror("错误", "请输入有效的网易云音乐用户ID（纯数字）")
            return

        # 构建完整URL
        url = f"https://music.163.com/#/user/event?id={user_id}"

        # 清空之前的结果
        self.articles = []
        self.article_listbox.delete(0, tk.END)
        self.count_label.config(text="已检测到 0 篇文章")

        self.status_var.set("开始加载页面...")
        self.crawling = True
        self.load_button.config(text="加载中...", state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        # 重置爬虫的终止标志
        self.crawler.stop_crawling = False

        # 启动爬虫线程
        self.crawler_thread = threading.Thread(target=self.run_crawler, args=(url,), daemon=True)
        self.crawler_thread.start()

    def run_crawler(self, url):
        """运行爬虫的独立线程"""
        # 创建新的事件循环
        try:
            # 如果存在旧的事件循环，先关闭它
            old_loop = asyncio.get_event_loop()
            if old_loop.is_running():
                old_loop.close()
        except:
            pass

        # 创建新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # 创建字符串IO对象来捕获输出
        string_io = io.StringIO()

        class OutputRedirector:
            def __init__(self, ui, string_io):
                self.ui = ui
                self.string_io = string_io
                self.has_console = hasattr(sys, 'stdout') and sys.stdout is not None
                self.old_stdout = sys.stdout if self.has_console else None
                self.old_stderr = sys.stderr if self.has_console else None
            
            def write(self, message):
                if self.string_io:
                    self.string_io.write(message)
                if self.has_console and self.old_stdout:
                    try:
                        self.old_stdout.write(message)
                    except:
                        pass
                if message.strip():
                    self.ui.add_update('status', message=message.strip())
                    self.ui.console_output.append(message.strip())
            
            def flush(self):
                if self.has_console and self.old_stdout:
                    try:
                        self.old_stdout.flush()
                    except:
                        pass
            
            def __enter__(self):
                if self.has_console:
                    sys.stdout = self
                    sys.stderr = self
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                if self.has_console:
                    sys.stdout = self.old_stdout
                    sys.stderr = self.old_stderr

        with OutputRedirector(self, string_io):
            try:
                # 添加调试信息
                print("[UI] 开始运行爬虫...")
                print(f"[UI] URL: {url}")

                # 运行爬虫
                loop.run_until_complete(self.crawler.crawl(url, self))
                print("[UI] 爬虫运行完成")

            except Exception as e:
                error_msg = f"爬取失败: {str(e)}"
                print(f"[UI] {error_msg}")
                if not getattr(sys, 'frozen', False):
                    traceback.print_exc()

                # 获取详细的错误信息
                error_details = string_io.getvalue()

                # 更新状态
                self.add_update("status", message=error_msg)

                # 在主线程中显示错误对话框
                self.master.after(
                    0, lambda: self.show_error_dialog(error_msg, error_details)
                )

            finally:
                try:
                    # 安全关闭事件循环
                    pending = asyncio.all_tasks(loop)
                    for task in pending:
                        task.cancel()

                    loop.run_until_complete(
                        asyncio.gather(*pending, return_exceptions=True)
                    )
                    loop.close()
                except:
                    pass

                self.crawling = False
                self.master.after(
                    0, lambda: self.load_button.config(text="加载", state=tk.NORMAL)
                )
                self.master.after(0, lambda: self.stop_button.config(state=tk.DISABLED))

    def show_error_dialog(self, error_msg, error_details):
        """显示详细的错误对话框"""
        # 创建一个新的窗口
        error_window = tk.Toplevel(self.master)
        error_window.title("错误详情")
        error_window.geometry("600x400")

        # 错误信息标签
        tk.Label(error_window, text=error_msg, fg="red", font=("Arial", 12)).pack(
            pady=10
        )

        # 创建文本框显示详细信息
        text_frame = tk.Frame(error_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        error_text = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        error_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=error_text.yview)

        # 插入错误详情
        error_text.insert(tk.END, "=== 错误详情 ===\n\n")
        error_text.insert(tk.END, error_details)
        error_text.config(state=tk.DISABLED)

        # 关闭按钮
        tk.Button(error_window, text="关闭", command=error_window.destroy).pack(pady=10)

        # 复制按钮
        def copy_error():
            self.master.clipboard_clear()
            self.master.clipboard_append(error_details)
            messagebox.showinfo("复制成功", "错误信息已复制到剪贴板")

        tk.Button(error_window, text="复制错误信息", command=copy_error).pack(pady=5)

    def set_max_range(self):
        count = len(self.articles)
        if count > 0:
            self.start_range.delete(0, tk.END)
            self.start_range.insert(0, "1")
            self.end_range.delete(0, tk.END)
            self.end_range.insert(0, str(count))

            if not self.crawling:
                self.status_var.set(f"已设置范围: 1 到 {count}")
            else:
                print(f"已设置范围: 1 到 {count}")

    def get_selected_articles(self):
        try:
            start = max(1, int(self.start_range.get()))
            end = min(len(self.articles), int(self.end_range.get()))

            if start > end or start > len(self.articles):
                messagebox.showerror("错误", "请输入有效的范围")
                return []

            return self.articles[start - 1 : end]
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字范围")
            return []

    def copy_text(self):
        selected_articles = self.get_selected_articles()

        if not selected_articles:
            return

        self.status_var.set("正在处理文本...")

        threading.Thread(
            target=self.process_text_copy, args=(selected_articles,), daemon=True
        ).start()

    def process_text_copy(self, articles):
        try:
            copy_text = copy_to_clipboard(articles)

            self.master.clipboard_clear()
            self.master.clipboard_append(copy_text)

            self.master.after(
                0, lambda: self.status_var.set(f"已复制 {len(articles)} 篇文章")
            )

            self.master.after(0, lambda: self.copy_button.config(text="已复制!"))
            self.master.after(1500, lambda: self.copy_button.config(text="复制文本"))
        except Exception as e:
            self.master.after(
                0, lambda: messagebox.showerror("错误", f"复制失败: {str(e)}")
            )
            self.master.after(0, lambda: self.status_var.set("复制失败"))

    def export_html(self):
        selected_articles = self.get_selected_articles()

        if not selected_articles:
            return

        self.settings["imageSize"] = int(self.size_spinbox.get())
        self.settings["useBase64Images"] = self.base64_var.get()

        self.status_var.set("正在处理导出...")
        self.export_button.config(text="处理中...")

        threading.Thread(
            target=self.process_html_export,
            args=(selected_articles, self.settings),
            daemon=True,
        ).start()

    def process_html_export(self, articles, settings):
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".html",
                filetypes=[("HTML文件", "*.html"), ("所有文件", "*.*")],
                title="保存HTML文件",
            )

            if not file_path:
                self.master.after(0, lambda: self.status_var.set("导出已取消"))
                self.master.after(0, lambda: self.export_button.config(text="导出HTML"))
                return

            if settings["useBase64Images"]:
                self.master.after(0, lambda: self.status_var.set("正在准备处理图片..."))

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                loop.run_until_complete(
                    export_to_html(articles, file_path, settings, self)
                )
            finally:
                loop.close()

        except Exception as e:
            self.master.after(
                0, lambda: messagebox.showerror("错误", f"导出失败: {str(e)}")
            )
            self.master.after(0, lambda: self.status_var.set(f"导出失败: {str(e)}"))
        finally:
            self.master.after(0, lambda: self.export_button.config(text="导出HTML"))

    def open_changelog(self):
        """打开更新日志页面"""
        webbrowser.open(self.PROJECT_URL)

    def show_about(self):
        """显示关于作者窗口"""
        about_window = tk.Toplevel(self.master)
        about_window.title("关于作者")
        about_window.transient(self.master)
        about_window.grab_set()

        # 设置窗口大小
        about_window.geometry("500x260")

        # 窗口居中
        about_window.update_idletasks()
        width = about_window.winfo_width()
        height = about_window.winfo_height()
        x = (about_window.winfo_screenwidth() // 2) - (width // 2)
        y = (about_window.winfo_screenheight() // 2) - (height // 2)
        about_window.geometry(f"{width}x{height}+{x}+{y}")

        # 创建一个框架来容纳图片和按钮
        frame = ttk.Frame(about_window)
        frame.pack(fill=tk.BOTH, expand=True)

        # 加载二维码图片
        try:
            # 获取图片路径
            script_dir = os.path.dirname(os.path.abspath(__file__))
            qrcode_path = os.path.join(script_dir, "resources", "weixin.png")

            if os.path.exists(qrcode_path):
                img = Image.open(qrcode_path)
                img = img.resize((500, 182), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)

                img_label = ttk.Label(frame, image=photo)
                img_label.image = photo  # 保持引用防止被垃圾回收
                img_label.pack(pady=10)

                text_label = ttk.Label(
                    frame, text="扫码关注公众号，支持作者更新~", font=("微软雅黑", 10)
                )
                text_label.pack(pady=5)
            else:
                error_label = ttk.Label(
                    frame, text="找不到二维码图片", foreground="red"
                )
                error_label.pack(pady=20)
        except Exception as e:
            error_label = ttk.Label(
                frame, text=f"无法加载图片: {str(e)}", foreground="red"
            )
            error_label.pack(pady=20)
