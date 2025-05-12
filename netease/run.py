"""
网易云音乐动态备份工具启动脚本
"""

import tkinter as tk
from netease.crawler import NetEaseCrawler
from netease.ui import NetEaseMusicUI
import asyncio
import sys
import traceback
import signal
import atexit


def cleanup(crawler):
    """清理函数"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(crawler.close())
        loop.close()
    except:
        pass


def signal_handler(signum, frame):
    """信号处理函数"""
    print("\n收到退出信号，正在清理...")
    sys.exit(0)


def main():
    """应用程序入口点"""
    crawler = None
    
    try:
        # 设置信号处理
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # 设置异常处理
        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            
            print("未捕获的异常:")
            traceback.print_exception(exc_type, exc_value, exc_traceback)
        
        sys.excepthook = handle_exception
        
        # 创建主窗口
        root = tk.Tk()
        root.title("网易云音乐动态备份工具")
        root.geometry("800x600")
        
        # 创建爬虫实例
        crawler = NetEaseCrawler()
        
        # 注册退出时的清理函数
        atexit.register(lambda: cleanup(crawler))
        
        # 创建UI实例，传入爬虫
        app = NetEaseMusicUI(root, crawler)
        
        # 启动主循环
        root.mainloop()
        
    except Exception as e:
        print(f"应用程序错误: {e}")
        traceback.print_exc()
    finally:
        # 确保关闭爬虫
        if crawler:
            cleanup(crawler)


if __name__ == "__main__":
    main()