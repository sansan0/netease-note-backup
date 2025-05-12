"""
浏览器管理模块，智能处理开发环境和打包环境的浏览器
"""
import os
import sys
import zipfile
import platform
import aiohttp
from pathlib import Path
import shutil
import subprocess
import traceback
import time

class BrowserManager:
    def __init__(self, debug_callback=None):
        self.debug_callback = debug_callback
        
        # 判断是否为打包环境
        self.is_frozen = getattr(sys, 'frozen', False)
        
        # 获取应用程序目录
        if self.is_frozen:
            self.app_dir = Path(sys.executable).parent
        else:
            self.app_dir = Path.cwd()
        
        # 设置浏览器目录
        self.local_browser_dir = self.app_dir / "browsers"
        self.chromium_dir = self.local_browser_dir / "chromium"
        
        # 操作系统相关设置
        self.platform = platform.system().lower()
        if self.platform == "windows":
            self.executable_name = "chrome.exe"
        elif self.platform == "darwin":  # macOS
            self.executable_name = "Chromium.app/Contents/MacOS/Chromium"
        else:  # Linux
            self.executable_name = "chrome"
        
        # Playwright 默认浏览器路径
        self.playwright_browsers_path = self._get_playwright_browsers_path()
        
        self.executable_path = None
        
        # 添加调试日志
        self._debug_log(f"[BrowserManager] 初始化:")
        self._debug_log(f"  - 是否打包环境: {self.is_frozen}")
        self._debug_log(f"  - 应用目录: {self.app_dir}")
        self._debug_log(f"  - 本地浏览器目录: {self.local_browser_dir}")
        self._debug_log(f"  - 目标chromium目录: {self.chromium_dir}")
        self._debug_log(f"  - Playwright浏览器目录: {self.playwright_browsers_path}")
        
        # 检查并修复遗留的临时目录
        self._fix_temp_directories()
    
    def _debug_log(self, message):
        """输出调试信息"""
        print(message)
        if self.debug_callback:
            self.debug_callback(message)
    
    def _fix_temp_directories(self):
        """检查并修复临时目录问题"""
        temp_dir = self.local_browser_dir / "temp"
        
        # 如果temp目录存在，检查是否有chrome
        if temp_dir.exists():
            print(f"[BrowserManager] 发现临时目录: {temp_dir}")
            
            # 查找chrome-win目录
            chrome_win_dir = temp_dir / "chrome-win"
            if chrome_win_dir.exists() and (chrome_win_dir / "chrome.exe").exists():
                print(f"[BrowserManager] 在临时目录找到chrome: {chrome_win_dir}")
                
                # 如果chromium目录不存在，移动chrome-win到chromium
                if not self.chromium_dir.exists():
                    try:
                        print(f"[BrowserManager] 移动 {chrome_win_dir} -> {self.chromium_dir}")
                        shutil.move(str(chrome_win_dir), str(self.chromium_dir))
                        print(f"[BrowserManager] 移动成功")
                        
                        # 清理空的temp目录
                        if temp_dir.exists() and not list(temp_dir.iterdir()):
                            temp_dir.rmdir()
                            print(f"[BrowserManager] 删除空的temp目录")
                    except Exception as e:
                        print(f"[BrowserManager] 移动失败: {e}")
                else:
                    print(f"[BrowserManager] chromium目录已存在，跳过移动")
    
    def _get_playwright_browsers_path(self):
        """获取 Playwright 默认浏览器路径"""
        # 环境变量优先
        env_path = os.environ.get('PLAYWRIGHT_BROWSERS_PATH')
        if env_path:
            return Path(env_path)
        
        if self.platform == "windows":
            return Path(os.environ.get('USERPROFILE', '')) / 'AppData' / 'Local' / 'ms-playwright'
        elif self.platform == "darwin":
            return Path.home() / 'Library' / 'Caches' / 'ms-playwright'
        else:  # Linux
            return Path.home() / '.cache' / 'ms-playwright'
    
    def find_browser(self):
        """按优先级查找浏览器"""
        print(f"[BrowserManager] 开始查找浏览器...")
        
        # 优先级1：打包应用的本地浏览器目录
        if self.is_frozen and self.find_browser_in_dir(self.chromium_dir):
            print(f"[BrowserManager] 在打包目录找到浏览器: {self.executable_path}")
            return self.executable_path
        
        # 优先级2：本地浏览器目录（所有环境）
        if self.find_browser_in_dir(self.chromium_dir):
            print(f"[BrowserManager] 在本地目录找到浏览器: {self.executable_path}")
            return self.executable_path
        
        # 优先级3：检查temp目录（可能解压未完成）
        temp_dir = self.local_browser_dir / "temp"
        if temp_dir.exists():
            for item in temp_dir.iterdir():
                if item.is_dir() and self.find_browser_in_dir(item):
                    print(f"[BrowserManager] 在临时目录找到浏览器: {self.executable_path}")
                    return self.executable_path
        
        # 优先级4：Playwright 默认安装的浏览器（仅开发环境）
        if not self.is_frozen and self.playwright_browsers_path.exists():
            print(f"[BrowserManager] 搜索Playwright目录: {self.playwright_browsers_path}")
            for chromium_dir in self.playwright_browsers_path.glob("chromium-*"):
                if self.find_browser_in_dir(chromium_dir):
                    print(f"[BrowserManager] 在Playwright目录找到浏览器: {self.executable_path}")
                    return self.executable_path
        
        print(f"[BrowserManager] 未找到浏览器")
        return None
    
    def find_browser_in_dir(self, directory):
        """在指定目录中查找浏览器可执行文件"""
        if not directory or not directory.exists():
            print(f"[BrowserManager] 目录不存在: {directory}")
            return False
        
        print(f"[BrowserManager] 在目录中查找: {directory}")
        
        # Windows
        if self.platform == "windows":
            # 直接检查chrome.exe
            chrome_exe = directory / "chrome.exe"
            if chrome_exe.exists():
                self.executable_path = chrome_exe
                print(f"[BrowserManager] 找到可执行文件: {self.executable_path}")
                return True
            
            # 递归搜索
            for root, _, files in os.walk(directory):
                if self.executable_name in files:
                    self.executable_path = Path(root) / self.executable_name
                    print(f"[BrowserManager] 找到可执行文件: {self.executable_path}")
                    return True
        
        # macOS
        elif self.platform == "darwin":
            app_path = directory / "Chromium.app"
            if app_path.exists():
                self.executable_path = directory / self.executable_name
                if os.path.exists(self.executable_path):
                    print(f"[BrowserManager] 找到可执行文件: {self.executable_path}")
                    return True
        
        # Linux
        else:
            for root, _, files in os.walk(directory):
                if self.executable_name in files:
                    exe_path = Path(root) / self.executable_name
                    if os.access(exe_path, os.X_OK):  # 检查是否可执行
                        self.executable_path = exe_path
                        print(f"[BrowserManager] 找到可执行文件: {self.executable_path}")
                        return True
        
        return False
    
    def is_browser_installed(self):
        """检查是否有可用的浏览器"""
        return self.find_browser() is not None
    
    def get_executable_path(self):
        """获取浏览器可执行文件路径"""
        browser_path = self.find_browser()
        return str(browser_path) if browser_path else None
    
    def get_download_url(self):
        """获取 Chromium 下载 URL"""
        # Playwright 使用的 Chromium 版本
        revision = "1148"  # 对应 Playwright 1.52.0
        
        base_url = "https://playwright.azureedge.net/builds/chromium"
        
        if self.platform == "windows":
            if platform.machine().endswith('64'):
                return f"{base_url}/{revision}/chromium-win64.zip"
            else:
                return f"{base_url}/{revision}/chromium-win32.zip"
        elif self.platform == "darwin":
            if platform.machine() == "arm64":
                return f"{base_url}/{revision}/chromium-mac-arm64.zip"
            else:
                return f"{base_url}/{revision}/chromium-mac.zip"
        else:  # Linux
            return f"{base_url}/{revision}/chromium-linux.zip"
    
    async def download_browser(self, progress_callback=None):
        """下载浏览器到本地目录"""
        try:
            url = self.get_download_url()
            self.local_browser_dir.mkdir(parents=True, exist_ok=True)
            
            zip_path = self.local_browser_dir / "chromium.zip"
            
            print(f"[BrowserManager] 开始下载浏览器: {url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    
                    total_size = int(response.headers.get('Content-Length', 0))
                    downloaded = 0
                    
                    with open(zip_path, 'wb') as file:
                        async for chunk in response.content.iter_chunked(8192):
                            file.write(chunk)
                            downloaded += len(chunk)
                            
                            if progress_callback and total_size > 0:
                                progress = (downloaded / total_size) * 100
                                await progress_callback(progress, downloaded, total_size)
            
            print(f"[BrowserManager] 下载完成: {zip_path}")
            return zip_path
            
        except Exception as e:
            print(f"[BrowserManager] 下载失败: {e}")
            traceback.print_exc()
            if zip_path.exists():
                zip_path.unlink()
            raise e
    
    def extract_browser(self, zip_path):
        """解压浏览器"""
        try:
            print(f"[BrowserManager] 开始解压: {zip_path}")
            
            # 确保zip文件存在
            if not zip_path.exists():
                raise Exception(f"ZIP文件不存在: {zip_path}")
            
            # 创建临时目录
            temp_dir = self.local_browser_dir / "temp"
            if temp_dir.exists():
                print(f"[BrowserManager] 清理旧的临时目录")
                shutil.rmtree(temp_dir)
            temp_dir.mkdir(exist_ok=True)
            
            # 解压文件
            with zipfile.ZipFile(zip_path, 'r') as zip_file:
                print(f"[BrowserManager] 解压到临时目录: {temp_dir}")
                zip_file.extractall(temp_dir)
            
            # 延迟一下确保文件句柄释放
            time.sleep(0.5)
            
            # 尝试删除zip文件
            try:
                zip_path.unlink()
                print(f"[BrowserManager] 删除zip文件成功")
            except Exception as e:
                print(f"[BrowserManager] 删除zip文件失败: {e}")
            
            # 找到解压出的chrome目录
            extracted_items = list(temp_dir.iterdir())
            print(f"[BrowserManager] 解压出的项目: {[item.name for item in extracted_items]}")
            
            # 查找包含chrome.exe的目录
            chrome_dir = None
            for item in extracted_items:
                if item.is_dir():
                    # 检查是否包含chrome.exe
                    if (item / "chrome.exe").exists():
                        chrome_dir = item
                        break
                    # 递归检查子目录
                    for subdir in item.iterdir():
                        if subdir.is_dir() and (subdir / "chrome.exe").exists():
                            chrome_dir = subdir
                            break
            
            if not chrome_dir:
                raise Exception("未找到chrome.exe")
            
            print(f"[BrowserManager] 找到Chrome目录: {chrome_dir}")
            
            # 如果chromium目录存在，先删除
            if self.chromium_dir.exists():
                print(f"[BrowserManager] 删除旧的chromium目录")
                shutil.rmtree(self.chromium_dir)
            
            # 移动chrome目录到chromium目录
            print(f"[BrowserManager] 移动 {chrome_dir} -> {self.chromium_dir}")
            shutil.move(str(chrome_dir), str(self.chromium_dir))
            
            # 清理临时目录
            if temp_dir.exists():
                try:
                    shutil.rmtree(temp_dir)
                    print(f"[BrowserManager] 清理临时目录成功")
                except Exception as e:
                    print(f"[BrowserManager] 清理临时目录失败: {e}")
            
            # 验证安装
            if self.find_browser_in_dir(self.chromium_dir):
                print(f"[BrowserManager] 浏览器安装成功: {self.executable_path}")
                return True
            else:
                raise Exception("浏览器安装验证失败")
                
        except Exception as e:
            print(f"[BrowserManager] 解压失败: {e}")
            traceback.print_exc()
            raise e
    
    async def ensure_browser(self, progress_callback=None):
        """确保浏览器可用，如果不存在则下载"""
        # 首先检查并修复临时目录
        self._fix_temp_directories()
        
        if self.is_browser_installed():
            return self.get_executable_path()
        
        # 下载浏览器
        if progress_callback:
            await progress_callback(0, 0, 0)  # 开始下载
        
        zip_path = await self.download_browser(progress_callback)
        self.extract_browser(zip_path)
        
        # 再次检查是否安装成功
        if self.is_browser_installed():
            return self.get_executable_path()
        
        raise Exception("浏览器安装失败")
    
    def use_playwright_browser(self):
        """尝试使用 playwright install chromium 安装浏览器（仅开发环境）"""
        if self.is_frozen:
            return False
        
        try:
            # 运行 playwright install chromium
            result = subprocess.run(
                ["poetry", "run", "playwright", "install", "chromium"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # 重新检查浏览器
                return self.is_browser_installed()
            else:
                print(f"Playwright 安装失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"运行 playwright install 失败: {e}")
            return False